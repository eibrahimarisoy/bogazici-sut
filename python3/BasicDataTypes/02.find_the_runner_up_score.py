# Problem: https://www.hackerrank.com/challenges/find-second-maximum-number-in-a-list/problem
# Score: 10


n = int(input())
arr = set(list(map(int, input().split()))[:n])
print(sorted(arr)[-2])
