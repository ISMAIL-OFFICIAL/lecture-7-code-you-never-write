"""
check_payments.py

Reads a payments file, compares the total received against the
expected total, and reports whether anything is missing (or extra).

Expected file format:
    Expected Total: 500

    Ali,100
    Ahmed,100
    Sara,50
    Bilal,100
    John,100
"""

def read_payments(filepath):
    expected_total = None
    payments = []

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue  # skip blank lines

            if line.lower().startswith("expected total"):
                # Split on ":" and grab the number after it
                expected_total = float(line.split(":", 1)[1].strip())
            else:
                # A payment line looks like "Name,Amount"
                name, amount = line.split(",")
                payments.append((name.strip(), float(amount.strip())))

    return expected_total, payments


def main():
    filepath = "payments.txt"  # change this if your file has a different name/path

    expected_total, payments = read_payments(filepath)
    received_total = sum(amount for _, amount in payments)
    missing_amount = expected_total - received_total

    print("=" * 40)
    print("PAYMENT SUMMARY")
    print("=" * 40)

    for name, amount in payments:
        print(f"{name:<10} paid  {amount:.2f}")

    print("-" * 40)
    print(f"Expected Total : {expected_total:.2f}")
    print(f"Received Total : {received_total:.2f}")

    if missing_amount > 0:
        print(f"Missing Amount : {missing_amount:.2f}  <-- short by this much")
    elif missing_amount < 0:
        print(f"Extra Amount   : {abs(missing_amount):.2f}  <-- overpaid by this much")
    else:
        print("Status         : Fully paid, no missing amount!")

    print("=" * 40)


if __name__ == "__main__":
    main()