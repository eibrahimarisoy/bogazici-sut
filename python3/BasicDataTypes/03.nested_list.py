# Problem: https://www.hackerrank.com/challenges/nested-list/problem
# Score: 10


n = int(input())
marksheet = [[input(), float(input())] for _ in range(n)]
sorted_list = list(sorted(set(x[1] for x in marksheet)))

for name in sorted(marksheet):
    if name[1] == sorted_list[1]:
        print(name[0])
