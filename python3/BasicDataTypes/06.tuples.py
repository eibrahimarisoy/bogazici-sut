# Problem: https://www.hackerrank.com/challenges/python-tuples/problem
# Score: 10


n = int(input())
integer_list = map(int, input().split())
print(hash(tuple(integer_list)))
