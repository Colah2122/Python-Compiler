
from abc import ABC, abstractmethod
import re

debug = 0

class JExpr(ABC):
    def ppt(self):
        return self.__str__();
    @abstractmethod
    def __str__(self):
        pass
    @abstractmethod
    def interp(self):
        pass

class JNum(JExpr):
    def __init__(self, eNum):
        self.eNum = int(eNum)
    def __str__(self):
        return str(self.eNum)
    def interp(self):
        return self.eNum

class JPlus(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight
    def __str__(self):
        return "(+ " + str(self.eLeft) + " " + str(self.eRight) + ")"
    def interp(self):
        return self.eLeft.interp() + self.eRight.interp()

class JMult(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight
    def __str__(self):
        return "(* " + str(self.eLeft) + " " + str(self.eRight) + ")"
    def interp(self):
        return self.eLeft.interp() * self.eRight.interp()

def JCheck(e, expAns):
    actAns = e.interp()
    isCorrect = actAns == expAns
    result = "CORRECT!!" if isCorrect else "FAILURE!!"
    print(e.ppt(), " = ", actAns, " >>> ", result)
    return isCorrect

def parseList(tokens):
    if debug: print("tokens=", tokens)
    stack = []
    while len(tokens) > 0:
        x = tokens.pop(0)
        if x == "(":
            stack.append(parseList(tokens))
        elif x == ")":
            return stack
        elif re.match(r"[-+]?\d+$", x) is not None:
            stack.append(int(x))
        else:
            stack.append(x)
    return stack[0]

def reader(e):
    withSpace = e.replace("(", " ( ").replace(")", " ) ").replace("  ", " ").strip()
    if debug: print("withSpace=", withSpace)
    tokens = withSpace.split()
    se = parseList(tokens)
    return se

e = []
e.append(["9", 9])
e.append(["(+ 2 3)", 5])
e.append(["(* 2 -7)", -14])
e.append(["(+ 1 (* 2 -5))", -9])
e.append(["(+ 1 (* 1 (* 1 1)))", 2])
e.append(["(+ 1 (+ 5 (* 2 (* 5 -5))))", -44])
e.append(["(+ 3 (+ 2 (+ (* 3 4) (* -1 4))))", 13])
e.append(["(+ 5 (+ 1 (* 2 (* 7 5))))", 76])
e.append(["(+ 5 (+ (+ 2 (+ 7 5)) 81))", 100])
e.append(["(+ (* 2 3) (+ (+ (+ 2 -4) 2) (* 2 3)))", 12])
e.append(["(* (+ 1 (* 2 5)) (* 14 (+ 1 (+ 2 5))))", 1232])
e.append(["(+ (* 2 3) (+ (+ (+ (+ -3 (* -1 9)) -4) 2) (* 2 3)))", -2])


print()
print("="*80)
print(">"*8, "task 6: Convert your J0 test-suite into Sexprs")
print("="*80)

for l in e:
    print("-"*50)
    print("str=",l[0])
    se = reader(l[0])
    print("se=", se)
