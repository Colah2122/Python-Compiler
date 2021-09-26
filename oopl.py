
from abc import ABC, abstractmethod
import re
import sys

debug = 1
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

def interpSS(se):
    if debug: print("se=", se)
    flat = flatten(se)
    if debug: print("flat=", flat)
    cnt = 1
    while True:
        print(">"*10, "STEP #", cnt, ">"*20)
        cnt += 1
        print("flat=",flat)
        c, r = findRedex(flat)
        print("context=",c)
        print("redex=",r)
        if r == []:
            break
        e = desugar(r)
        ans = e.interp()
        print("ans=", ans)
        flat = plugHole(ans, c)
    return c

def myStr(l):
    if isinstance(l, list):
        if len(l) == 0: return "[]"
        s1 = " ".join(str(x) for x in l)
        if l[0] != "[": s1 = "[" +  s1
        if l[-1] != "]": s1 = s1 + "]"
        s2 = s1.replace("[ ", "[").replace(" ]", "]")
        return s2
    return str(l)

class frame(ABC):
    def ppt(self):
        return self.__str__();
    @abstractmethod
    def __str__(self):
        pass

class kret(frame):
    def __str__(self):
        return "kret"

class kif(frame):
    def __init__(self, eTrue, eFalse, k):
        if not isinstance(k, frame): sys.exit("k must be a frame?")
        self.eTrue = eTrue
        self.eFalse = eFalse
        self.frame = k
    def __str__(self):
        return "kif(" + myStr(self.eTrue) + ", " + myStr(self.eFalse) + ", " + str(self.frame) + ")"

class kapp(frame):
    def __init__(self, lVal, lExpr, k):
        if not isinstance(lVal, list): sys.exit("lVal must be a list?")
        if not isinstance(lExpr, list): sys.exit("lExpr must be a list?")
        if not isinstance(k, frame): sys.exit("k must be a frame?")
        self.lVal = lVal
        self.lExpr = lExpr
        self.frame = k
    def __str__(self):
        return "kapp(" + myStr(self.lVal) + ", " + myStr(self.lExpr) + ", " + str(self.frame) + ")"

se1 = []
se1.append([19, 19])
se1.append([[">=", 5, 3], True])
se1.append([[">=", ["+", 8, ["*", 1, 3, 1, 1, 2]], 3], True])
se1.append([[">=", 3, 5], False])
se1.append([["+", 5, ["*", 2, -3]], -1])
se1.append([["if", ["<", 1, 3], ["if", [">", 4, 2], -3, -5], 15], -3])
se1.append([["if", [">", 1, 3], ["if", [">", 4, 2], -3, -5], ["if", ["<", ["+", 2, 2], ["*", 3, 1]], -31, 4]], 4])
se1.append([["if", ["<", ["-", 2, 1], 3], ["+", 4, 5], -3], 9])
se1.append([["+", 1, ["if", ["+", 2, 2], 3, 4]], 4])
se1.append([["+", 1, ["if", ["+", 2, -2], 3, 4]], 5])
se1.append([["if", ["<", ["-", 2, 1], 3], ["+", 4, ["-", 5, -3]], ["if", ["=", 4, 4], ["+", 3, 2], 7]], 12])
se1.append([["/", 9, ["if", ["-", 2, -2], 3, 4]], 3])
se1.append([["+", 1, ["*", 2, 10], -3, 5, ["if", ["=", 3, 3], 3, ["+", 4, 4]]], 26])
se1.append([["if", ["<", 1, 3], ["-", 5, 4], 6], 1])
se1.append([["if", ["<", 1, 3], 15, ["-", 5, ["+", 2, 2]]], 15])


print()
print("="*80)
print(">"*8, "task 18: Define data structures to represent continuations")
print("="*80)

a = kret()
b = kif(5, 7, a)
c = kapp([], ["+", 3, 4], b)

print("a=", a)
print("b=", b)
print("c=", c)
