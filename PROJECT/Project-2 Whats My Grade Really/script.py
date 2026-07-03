assignments = [80, 90, 85]
quizzes = [70, 75]
midterm = 88

# Weights
assignment_weight = 0.30
quiz_weight = 0.20
midterm_weight = 0.20
final_weight = 0.30

# Averages
assignment_avg = sum(assignments) / len(assignments)
quiz_avg = sum(quizzes) / len(quizzes)

# Current contribution (without final)
current_points = (
    assignment_avg * assignment_weight
    + quiz_avg * quiz_weight
    + midterm * midterm_weight
)

print("Assignment Average:", round(assignment_avg, 2))
print("Quiz Average:", round(quiz_avg, 2))
print("Current Points Earned:", round(current_points, 2))

# Target overall grade
target_grade = 90

needed_final = (target_grade - current_points) / final_weight

if needed_final > 100:
    print("\nTarget Grade:", target_grade)
    print("Result: Achieving this grade is not possible because you would need", round(needed_final, 2), "on the final exam.")
else:
    print("\nTarget Grade:", target_grade)
    print("Score Needed on Final Exam:", round(needed_final, 2))