
from abc import ABC, abstractmethod
import re
import sys

debug = 0
primAll = ("+", "*", "/", "-", "<=", "<", "=", ">", ">=")

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

class JCond(JExpr):
    def __init__(self, eCond, eTrue, eFalse):
        self.eCond = eCond
        self.eTrue = eTrue
        self.eFalse = eFalse
    def __str__(self):
        return "(if " + str(self.eCond) + " " + str(self.eTrue) + " " + str(self.eFalse) + ")"
    def interp(self):
        ek = self.eTrue if bool(self.eCond.interp()) == True else self.eFalse
        return ek.interp()

class JDelta(JExpr):
    def __init__(self, prim, eLeft, eRight):
        self.prim = prim
        self.eLeft = eLeft
        self.eRight = eRight
        if self.prim not in primAll: sys.exit(self.prim + " not supported?")
    def __str__(self):
        return "(" + str(self.prim) + " " + str(self.eLeft) + " " + str(self.eRight) + ")"
    def interp(self):
        if self.prim == "+":
            return self.eLeft.interp() + self.eRight.interp()
        elif self.prim == "*":
            return self.eLeft.interp() * self.eRight.interp()
        elif self.prim == "/":
            return int(self.eLeft.interp() / self.eRight.interp())
        elif self.prim == "-":
            return self.eLeft.interp() - self.eRight.interp()
        elif self.prim == "<=":
            return self.eLeft.interp() <= self.eRight.interp()
        elif self.prim == "<":
            return self.eLeft.interp() < self.eRight.interp()
        elif self.prim == "=":
            return self.eLeft.interp() == self.eRight.interp()
        elif self.prim == ">":
            return self.eLeft.interp() > self.eRight.interp()
        elif self.prim == ">=":
            return self.eLeft.interp() >= self.eRight.interp()
        else:
            sys.exit(self.prim + " not implemented?")

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
        elif myLen == 3 and mySym in primAll:
            return JDelta(mySym, desugar(se[1]), desugar(se[2]))
        elif myLen == 4 and mySym in "if":
            return JCond(desugar(se[1]), desugar(se[2]), desugar(se[3]))
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

def flatten(aList):
    result = []
    if isinstance(aList, int):
        return [aList]
    for element in aList:
        if hasattr(element, "__iter__") and not isinstance(element, str):
            result.extend(["["] + flatten(element) + ["]"])
        else:
            result.append(element)
    return result

def plugHole(ans, context):
    if debug: print("context=",context)
    i = context.index("Hole")
    context[i] = ans
    return ans if i == 0 else context

def last(aList, item):
    return len(aList) - list(reversed(aList)).index(item) -  1 if item in aList else -1

def findRedex(term):
    if debug: print("input=", term)
    if isinstance(term, int):
        return term, []
    if isinstance(term, list):
        start = last(term,"[") + 1
        if start == 0:
            return ["Hole"], term
        stop = term.index("]",start)
        redex = term[start:stop]
        term[start-1] = "Hole"
        del term[start:stop+1]
        return term, redex
    else:
        sys.exit("can't findRedex?")

se1 = []
se1.append([19, 19])
se1.append([[">=", 5, 3], True])
se1.append([[">=", ["+", 8, 9], 3], True])
se1.append([[">=", 3, 5], False])
se1.append([["if", ["<", 1, 3], 15, -3], 15])
se1.append([["if", ["<", 1, 3], ["-", 5, 4], 6], 1])
se1.append([["+", 5, ["*", 2, -3]], -1])
se1.append([["if", ["<", 1, 3], ["if", [">", 4, 2], -3, -5], 15], -3])
se1.append([["if", [">", 1, 3], ["if", [">", 4, 2], -3, -5], ["if", ["<", ["+", 2, 2], ["*", 3, 1]], -31, 4]], 4])
se1.append([["if", ["<", ["-", 2, 1], 3], ["+", 4, 5], -3], 9])
se1.append([["+", 1, ["if", ["+", 2, 2], 3, 4]], 4])
se1.append([["+", 1, ["if", ["+", 2, -2], 3, 4]], 5])
se1.append([["if", ["<", ["-", 2, 1], 3], ["+", 4, ["-", 5, -3]], ["if", ["=", 4, 4], ["+", 3, 2], 7]], 3])
se1.append([["/", 9, ["if", ["-", 2, -2], 3, 4]], 3])


print()
print("="*80)
print(">"*8, "task 14: Implement find-redex, a function that breaks a term into a context and a redex")
print("="*80)

for l in se1:
    print("-"*50)
    term = flatten(l[0])
    print("term=",term)
    c, r = findRedex(term)
    print("context=",c)
    print("redex=",r)
