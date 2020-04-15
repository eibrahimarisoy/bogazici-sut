# Problem: https://www.hackerrank.com/challenges/python-lists/problem
# Score: 10

n = int(input())
arr = []
for i in range(n):
    command = input()
    if command == "print":
        print(arr)
    elif command == "sort":
        arr = sorted(arr)
    elif command == "pop":
        arr.pop()
    elif command == "reverse":
        arr.reverse()
    elif "append" in command:
        arr.append(int(command.split()[1]))
    elif "remove" in command:
        arr.remove(int(command.split()[1]))
    elif "insert" in command:
        arr.insert(int(command.split()[1]), int(command.split()[2]))
