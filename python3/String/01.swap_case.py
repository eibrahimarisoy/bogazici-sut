# Problem: https://www.hackerrank.com/challenges/swap-case/problem
# Score: 10


def swap_case(s):
    output = ""
    for i in s:
        if i.isupper():
            output += i.lower()
        else:
            output += i.upper()
    return output


if __name__ == "__main__":
    s = input()
    result = swap_case(s)
    print(result)
