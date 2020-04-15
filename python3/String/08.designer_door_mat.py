# Problem: https://www.hackerrank.com/challenges/designer-door-mat
# Score: 10


N, M = input().split()
N, M = int(N), int(M)
char = ".|."
for i in range(0, N):
    if i < N // 2:
        print((char * (2 * i + 1)).center(M, "-"))
    if i == N // 2:
        print("WELCOME".center(M, "-"))
    if i > (N // 2):
        print((char * (2 * (N - i) - 1)).center(M, "-"))
