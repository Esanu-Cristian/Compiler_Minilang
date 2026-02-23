A = {'a', 'b', 'c'}
B = {'x', 'y', 'z'}
C = {'1', '2', '3'}

def concatenate(s1, s2):
    return s1 + s2

def invers(s):
    return s[::-1]

def substituie(s, a, b):
    return s.replace(a, b)

def lungime(s):
    return len(s)

sirA = "acb"
sirB = "yzx"
sirC = "231"

print(f"Concatenare A+B: {concatenate(sirA, sirB)}")
print(f"Invers A: {invers(sirA)}")
print(f"Substituie 'a' cu 'x' in A: {substituie(sirA, 'a', 'x')}")
print(f"Lungime C: {lungime(sirC)}")
