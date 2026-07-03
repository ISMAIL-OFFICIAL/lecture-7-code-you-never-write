"""
Transaction Analyzer
=====================
Reads a CSV of transactions (Date, Description, Amount) and:
  1. Finds recurring subscriptions
  2. Finds duplicate payments
  3. Calculates total spending
  4. Creates a spending summary

Usage:
    python analyze_transactions.py transactions.csv
"""

import sys
import pandas as pd


def load_transactions(path: str) -> pd.DataFrame:
    """Read the CSV and clean it up a little."""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]  # date, description, amount
    df["date"] = pd.to_datetime(df["date"])
    df["description"] = df["description"].str.strip()
    df["amount"] = df["amount"].astype(float)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def find_recurring_subscriptions(df: pd.DataFrame, min_occurrences: int = 2) -> pd.DataFrame:
    """
    A 'recurring subscription' = the same merchant charging the same
    amount more than once (e.g. Netflix, -15, every month).

    We group by (description, amount) and keep groups that appear
    min_occurrences times or more.
    """
    grouped = df.groupby(["description", "amount"])

    rows = []
    for (desc, amount), group in grouped:
        if len(group) >= min_occurrences:
            dates = group["date"].sort_values()
            # Average number of days between charges (helps show it's "monthly", "weekly", etc.)
            if len(dates) > 1:
                avg_gap_days = dates.diff().dt.days.dropna().mean()
            else:
                avg_gap_days = None

            rows.append({
                "description": desc,
                "amount": amount,
                "occurrences": len(group),
                "first_charge": dates.min().date(),
                "last_charge": dates.max().date(),
                "avg_days_between_charges": round(avg_gap_days, 1) if avg_gap_days else None,
            })

    return pd.DataFrame(rows).sort_values("occurrences", ascending=False).reset_index(drop=True)


def find_duplicate_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    A 'duplicate payment' = the exact same merchant, amount, AND date
    appearing more than once. This usually signals an accidental
    double-charge rather than a normal recurring subscription.
    """
    dupes = df[df.duplicated(subset=["date", "description", "amount"], keep=False)]
    return dupes.sort_values(["date", "description"]).reset_index(drop=True)


def calculate_total_spending(df: pd.DataFrame) -> dict:
    """
    Total spending = sum of all negative amounts (money going out).
    We also report total income (positive amounts) and the net change.
    """
    spending = df.loc[df["amount"] < 0, "amount"].sum()
    income = df.loc[df["amount"] > 0, "amount"].sum()
    net = df["amount"].sum()

    return {
        "total_spending": round(abs(spending), 2),
        "total_income": round(income, 2),
        "net_change": round(net, 2),
    }


def build_spending_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    A per-merchant breakdown: how much was spent, how many times,
    and the average transaction size. Sorted from biggest spend to smallest.
    """
    spend_df = df[df["amount"] < 0].copy()
    spend_df["amount"] = spend_df["amount"].abs()

    summary = spend_df.groupby("description").agg(
        total_spent=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_transaction=("amount", "mean"),
    ).round(2)

    summary["percent_of_spending"] = (
        summary["total_spent"] / summary["total_spent"].sum() * 100
    ).round(1)

    return summary.sort_values("total_spent", ascending=False)


def main(csv_path: str):
    df = load_transactions(csv_path)

    print("=" * 60)
    print("RECURRING SUBSCRIPTIONS")
    print("=" * 60)
    recurring = find_recurring_subscriptions(df)
    print(recurring.to_string(index=False) if not recurring.empty else "None found.")

    print("\n" + "=" * 60)
    print("DUPLICATE PAYMENTS")
    print("=" * 60)
    duplicates = find_duplicate_payments(df)
    print(duplicates.to_string(index=False) if not duplicates.empty else "None found.")

    print("\n" + "=" * 60)
    print("TOTAL SPENDING")
    print("=" * 60)
    totals = calculate_total_spending(df)
    for k, v in totals.items():
        print(f"{k.replace('_', ' ').title()}: {v}")

    print("\n" + "=" * 60)
    print("SPENDING SUMMARY BY MERCHANT")
    print("=" * 60)
    summary = build_spending_summary(df)
    print(summary.to_string())

    # Save results to CSV files for easy sharing / opening in Excel
    recurring.to_csv("recurring_subscriptions.csv", index=False)
    duplicates.to_csv("duplicate_payments.csv", index=False)
    summary.to_csv("spending_summary.csv")
    print("\nSaved: recurring_subscriptions.csv, duplicate_payments.csv, spending_summary.csv")


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "transactions.csv"
    main(csv_file)