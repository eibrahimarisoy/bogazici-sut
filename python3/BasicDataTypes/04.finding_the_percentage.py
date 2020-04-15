# Problem: https://www.hackerrank.com/challenges/finding-the-percentage/problem
# Score: 10


n = int(input())
student_marks = {}
for _ in range(n):
    name, *line = input().split()
    scores = list(map(float, line))
    student_marks[name] = scores
query_name = input()

sum(student_marks.get(query_name)) / 3
