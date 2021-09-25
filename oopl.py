
from abc import ABC, abstractmethod
import re
import sys

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

def desugar(se):
    if debug and not isinstance(se, int): print("desugar=", se)
    if isinstance(se, int):
        return JNum(se)
    if isinstance(se, list):
        myLen = len(se)
        mySym = str(se[0])
        if isinstance(se[0], int):
            return JNum(se[0])
        elif myLen == 3 and mySym == "+":
            return JPlus(desugar(se[1]), desugar(se[2]))
        elif myLen == 3 and mySym == "*":
            return JMult(desugar(se[1]), desugar(se[2]))
        elif myLen == 3 and mySym == "-":
            return desugar(["+", se[1], ["*", -1, se[2]]])
        elif myLen == 2 and mySym == "-":
            return desugar(["*", -1, se[1]])
        elif myLen > 3 and mySym in ("+", "*", "-"):
            copy = se
            se =  copy.pop(1)
            return desugar([mySym, se, copy])
        else:
            sys.exit("can't generate JExpr?")

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

# test J0 surface
e.append(["(- 1 7)", -6])
e.append(["(+ 1 7 5 6 2 6)", 27])
e.append(["(* 1 3 4 2 2 2 )", 96])
e.append(["(- 7 (- 4 2))", 5])
e.append(["(- 7 (+ 4 2))", 1])

print()
print("="*80)
print(">"*8, "task 7: Implement a desugar function that converts Sexprs into J0")
print("="*80)

for l in e:
    print("-"*50)
    se = reader(l[0])
    j0 = desugar(se)
    JCheck(j0, l[1])
