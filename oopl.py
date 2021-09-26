
from abc import ABC, abstractmethod
import re
import sys
import copy

debug = 1
primAll = ("+", "*", "/", "-", "<=", "<", "=", ">", ">=")

myFunc = {}
myVar = {}
num = 0

def clearDict():
    global num
    num = 0
    myFunc.clear()
    myVar.clear()

def updateDict(name, varList, func):
    if not "".join(varList).islower(): sys.exit("func " + name + " MUST only have lower case variables!")
    if not name[0].isupper(): sys.exit("func " + name + " MUST start with a upper case letter!")
    if name in myFunc: sys.exit("func " + name + " already defined??")
    myFunc[name] = func
    myVar[name] = varList

def getFunction(name):
    if name not in myFunc: sys.exit("func " + name + " not found")
    expr = copy.deepcopy(myFunc[name])
    varList = copy.copy(myVar[name])
    if debug: print("FUNCTION", name + "(" + str(len(varList)) + "args)", ">>>>", expr)
    return varList, expr

def isFunction(name):
    return True if name in myFunc else False

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
    def __int__(self):
        return int(self.eNum)
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

class JFunc(JExpr):
    def __init__(self, func, argList):
        self.func = func
        self.argList = argList
        if not isFunction(self.func): sys.exit(self.func + " not defined?")
        if not isinstance(self.argList, list): sys.exit("argList is not a list?")
    def __str__(self):
        return "(" + self.func + str(self.argList) + ")"
    def interp(self):
        pass

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
            l = se
            se = l.pop(1)
            return desugar([mySym, se, l])
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

def findOppositeBracket(l):
    cnt = 0
    for i, item in enumerate(l):
        if item == "[": cnt += 1
        if item == "]": cnt -= 1
        if cnt == 0: return i
    return None

def eatExpression(l):
    e = []
    if len(l) > 0:
        if l[0] == "[":
            start = l.index("[")
            stop = findOppositeBracket(l)
            e = l[start:stop+1]
            del l[start:stop+1]
        else:
            e = l.pop(0)
    return e

def eatBracket(l):
    l.pop(0)
    sym = l.pop(0)
    l.pop()
    return sym

class ck0:
    def ppt(self):
        return self.__str__();
    def __init__(self, se):
        self.c = ["["] + flatten(se) + ["]"]
        self.k = kret()
    def __str__(self):
        aStr = " ".join(str(a) for a in self.c) if isinstance(self.c, list) else str(self.c)
        return "< " + aStr + ", " + str(self.k) + " >"
    def step(self):
        if isinstance(self.c, list) and self.c[0] == "[":
            if self.c[1] == "if":
                if debug: print("rule 1")
                eatBracket(self.c)
                ec = eatExpression(self.c)
                et = eatExpression(self.c)
                ef = eatExpression(self.c)
                self.k = kif(et, ef, self.k)
                self.c = ec
            elif self.c[1] in primAll:
                if debug: print("rule 4")
                c = eatBracket(self.c)
                self.k = kapp([], self.c, self.k)
                self.c = c
            else:
                if debug: print("rule 6")
                c = eatBracket(self.c)
                self.c = c
        elif isinstance(self.k, kapp):
            if len(self.k.lExpr) == 0:
                if debug: print("rule 6")
                l = list(reversed(self.k.lVal))
                l.append(self.c)
                j1 = desugar(l)
                self.c = j1.interp()
                self.k = self.k.frame
            else:
                if debug: print("rule 5")
                self.k.lVal.insert(0, self.c)
                self.c = eatExpression(self.k.lExpr)
        elif isinstance(self.k, kif):
            if bool(self.c) == True:
                if debug: print("rule 3")
                self.c = self.k.eTrue
                self.k = self.k.frame
            else:
                if debug: print("rule 2")
                self.c = self.k.eFalse
                self.k = self.k.frame
        else:
            sys.exit("can't step no more??")

def interpCK(se):
    st = ck0(se)
    print("inject")
    print("st=", st)
    cnt = 1
    while(True):
        st.step()
        print("st", cnt, "=", st)
        if isinstance(st.k, kret) and isinstance(st.c, int):
            break
        cnt += 1
    print("extract")
    print("ans=", st.c)
    return st.c

se1 = []
se1.append([19, 19])
se1.append([["=", 3, ["+", 2, 1]], True])
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
se1.append([[["define", ["Simple", "n"], ["+", ["*", "n", 3], 4]],
             ["Simple", 3]], 13]),
se1.append([[["define", ["Simple", "a", "b", "c", "d", "e", "f", "g", "h"], ["+", "a", "b", "c", "d", "e", "f", "g", "h"]],
             ["Simple", 1, 2, 3, 4, 5, 6, 7, 8]], 36]),
se1.append([[["define", ["P", "n"], ["if", [">", "n", 0], ["+", 1, ["Q", ["-", "n", 1]]], 1]],
             ["define", ["Q", "y"], ["if", [">", "y", 0], ["*", ["+", ["Q", ["-", "y", 1]], "y"], ["P", "y"]], 0]],
             ["+", ["Q", 3], ["P", 3]]], 70])
se1.append([[["define", ["Plus1", "n"], ["+", "n", 1]],
             ["define", ["Plus2", "n"], ["+", "n", 2]],
             ["define", ["Plus3", "n"], ["+", "n", 3]],
             ["define", ["Plus4", "n"], ["+", "n", 4]],
             ["define", ["Plus5", "n"], ["+", "n", 5]],
             ["+", ["Plus1", 5], ["Plus2", 4], ["Plus3", 3], ["Plus4", 2], ["Plus5", 1]]], 30])
se1.append([[["define", ["Plus1", "n"], ["+", "n", 1]],
             ["define", ["Plus2", "n"], ["+", "n", 2]],
             ["define", ["Plus3", "n"], ["+", "n", 3]],
             ["define", ["Plus4", "n"], ["+", "n", 4]],
             ["define", ["Plus5", "n"], ["+", "n", 5]],
             ["+", ["Plus1", ["Plus2", ["Plus3", ["Plus4", ["Plus5", 1]]]]], 12]], 28])
se1.append([[["define", ["ImN", "n"], ["n"]],
             ["+", ["ImN", 4], ["ImN", 3], ["ImN", -3], ["ImN", 6]]], 10])
se1.append([[["define", ["Factorial", "n"], ["if", ["=", "n", 1], 1, ["*", "n", ["Factorial", ["-", "n", 1]]]]],
             ["+", 1, ["Factorial", 6]]], 721])
se1.append([[["define", ["F", "x"], ["+", "x", 2]],
             ["define", ["G", "x", "y"], ["+", ["F", "x"],["F", "y"]]],
             ["G", ["+", 1, 2], 4]], 11])
se1.append([[["define", ["Double", "x"], ["+", "x", "x"]],
             ["define", ["Quad", "y"], ["Double", ["Double", "y"]]],
             ["Quad", ["+", 1, ["Double", 3]]]], 28])
se1.append([[["define", ["Sum1toN", "n"], ["if", ["=", "n", 1], 1, ["+", "n", ["Sum1toN", ["+", "n", -1]]]]],
             ["+", 1, ["Sum1toN", 5]]], 16])
se1.append([[["define", ["FibN", "n"], ["if", ["=", "n", 0], 0, ["if", ["=", "n", 1], 1, ["+", ["FibN", ["-", "n", 1]], ["FibN", ["-", "n", 2]]]]]],
             ["FibN", 5]], 5])
se1.append([[["define", ["IsEven", "n"], ["if", ["=", "n", 0], True, ["IsOdd", ["-", "n", 1]]]],
             ["define", ["IsOdd", "n"], ["if", ["=", "n", 0], False, ["IsEven", ["-", "n", 1]]]],
             ["IsOdd", [7]]], True])


print()
print("="*80)
print(">"*8, "task 22: Write a test-suite of a dozen J2 programs")
print("="*80)

for l in se1:
    clearDict()
    print()
    print("="*80)
    print("="*80)
    ans = l.pop()
    print(l, ">>>", ans, "?????")
