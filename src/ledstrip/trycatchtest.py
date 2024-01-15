def abc(a, b, c):
    try:
        print(1 / 0)
    except:
        print("inner catch")
        1 / 0


try:
    abc(1, 2, 3)
except:
    print("outer catch")
