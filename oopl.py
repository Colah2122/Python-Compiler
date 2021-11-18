
from abc import ABC, abstractmethod
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

class JApp(JExpr):
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

class JLambda(JExpr):
    def __init__(self, name, lVar, eBody):
        self.name = name
        self.lVar = copy.deepcopy(lVar)
        self.eBody = copy.deepcopy(eBody)
        if not isinstance(name, str): sys.exit("name must be a string?")
        if not isinstance(lVar, list): sys.exit("lVar must be a list?")
    def __str__(self):
        return "lambda_" + self.name + myStr(self.lVar) + " " +  myStr(self.eBody)
    def interp(self):
        sys.exit("never8")

def substitute1(num, var, expr):
    cnt = 0
    if not isinstance(expr, list): return cnt
    for i, e2 in enumerate(expr):
        if isinstance(e2, list):
            cnt += substitute1(num, var, e2)
        if e2 == var:
            expr[i] = num
            cnt += 1
    return cnt

def substituteList(envDict, expr):
    cnt = 0
    orig = copy.deepcopy(expr)
    for var, arg in envDict.items():
#        j2 = desugar(arg)
#        print("j2=",j2)
#        num = j2.interp()
        num = arg
#        if not isinstance(j2, JNum) and debug: print("****", "SIMPLIFY VARS", arg, "-->", num, "****")
        cnt2 = substitute1(num, var, expr)
        if debug and cnt2 > 0: print("PUT", num, "-->", var, "INTO", orig)
        cnt += cnt2
    return cnt

def CEKCheck(e, expAns):
    actAns = interpCEK(e)
    isCorrect = actAns == expAns
    result = "CORRECT!!" if isCorrect else "FAILURE!!"
    print(actAns, " = ", expAns, " >>> ", result)
    return isCorrect

def eatDefinitions(se):
    if not isinstance(se, list): return se
    cnt = 0
    for item in se:
        if isinstance(item, list) and item[0] == "define":
            cnt += 1
            if debug: print("func=",item)
            name = item[1].pop(0)
            updateDict(name, item[1], item[2])
        else:
            break
    if cnt > 0: se = se[cnt]
    if debug:
        if debug: print("-"*50)
        if debug: print("desugar=", se)
    return se

def desugar(se):
    if isinstance(se, int):
        return JNum(se)
    if isinstance(se, list):
        se = eatDefinitions(se)
        myLen = len(se)
        mySym = str(se[0])
        if isinstance(se[0], int):
            return JNum(se[0])
        elif myLen > 3 and mySym == "lambda":
            name = eatLambda(se)
            var = eatExpression(se)
            if var[0] == "[":
                var.pop(0)
                var.pop()
            return JLambda(name, var, se)
        elif myLen == 3 and mySym in primAll:
            return JApp(mySym, desugar(se[1]), desugar(se[2]))
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
    if not isinstance(aList, list):
        return aList
    result = []
    for element in aList:
        if isinstance(element, list):
            result.extend(flatten(element))
        else:
            result.append(element)
    return ["["] + result + ["]"]

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

def myStr(l):
    if isinstance(l, list):
        if len(l) == 0: return "[]"
        s1 = " ".join(str(x) for x in l)
        if l[0] != "[": s1 = "[" +  s1 + "]"
        s2 = s1.replace("[ ", "[").replace(" ]", "]")
        return s2
    if isinstance(l, dict):
        if len(l) == 0: return "mt"
        s3 = ','.join('->'.join((key,str(val))) for (key,val) in l.items())
        return "{" + s3 + "}"
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
    def __init__(self, eDict, eTrue, eFalse, k):
        if not isinstance(eDict, dict): sys.exit("eDict must be a dict?")
        if not isinstance(k, frame): sys.exit("k must be a frame?")
        self.env = copy.deepcopy(eDict)
        self.eTrue = copy.deepcopy(eTrue)
        self.eFalse = copy.deepcopy(eFalse)
        self.frame = k
    def __str__(self):
        return "kif(" + myStr(self.env) + ", " + myStr(self.eTrue) + ", " + myStr(self.eFalse) + ", " + str(self.frame) + ")"

class kapp(frame):
    def __init__(self, lVal, eDict, lExpr, k):
        if not isinstance(lVal, list): sys.exit("lVal must be a list?")
        if not isinstance(eDict, dict): sys.exit("eDict must be a dict?")
        if not isinstance(lExpr, list): sys.exit("lExpr must be a list?")
        if not isinstance(k, frame): sys.exit("k must be a frame?")
        self.lVal = copy.deepcopy(lVal)
        self.env = copy.deepcopy(eDict)
        self.lExpr = copy.deepcopy(lExpr)
        self.frame = k
    def __str__(self):
        return "kapp(" + myStr(self.lVal) + ", " + myStr(self.env) + ", " + myStr(self.lExpr) + ", " + str(self.frame) + ")"

def findOppositeBracket(l):
    cnt = 0
    for i, item in enumerate(l):
        if item == "[": cnt += 1
        if item == "]": cnt -= 1
        if cnt == 0: return i
    return None

def eatLambda(l):
    eatBracket(l)    # remove lambda
    name = "rec"
    if l[0] != "[":
        name = l.pop(0)
    return name

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
    if l[0] == "[":
        l.pop(0)
        l.pop()
    sym = l.pop(0)
    return sym

class closure:
    def ppt(self):
        return self.__str__();
    def __init__(self, lam, eDict):
        if not isinstance(lam, JLambda): sys.exit("lam must be JLambda?")
        if not isinstance(eDict, dict): sys.exit("eDict must be a dict?")
        self.lam = copy.deepcopy(lam)
        self.env = copy.deepcopy(eDict)
    def __str__(self):
        return "clo(" + str(self.lam) + ", " + myStr(self.env) + ")"

class cek0:
    def ppt(self):
        return self.__str__();
    def __init__(self, se):
        self.c = flatten(se)
        self.env = dict()
        self.k = kret()
    def __str__(self):
        aStr = " ".join(str(a) for a in self.c) if isinstance(self.c, list) else str(self.c)
        return "< " + aStr + ", " + myStr(self.env) + ", " + str(self.k) + " >"
    def dump(self):
        print("="*80)
        print("STEP")
        print("self.c=", self.c)
        print("type(self.c)=", type(self.c))
        print("self.env=", self.env)
        print("self.k=", self.k)
    def desugar(self):
        if isinstance(self.c, list) and (self.c[1] == "let" or self.c[0] == "let"):
            if debug: print(">>>> DESUGAR LET >>>>")
            eatBracket(self.c)    # remove let
            ec = eatExpression(self.c)
            var = eatBracket(ec)
            i = self.c.pop(0)    # remove in
            if i != "in": sys.exit("cant find let in??")
            eb = self.c
            lam = JLambda("rec", [var], eb)
            ec.insert(0,lam)
            ec.insert(0,"[")
            ec.append("]")
            self.c = ec
            if debug: print("self.c=", self.c)
        elif isinstance(self.c, list) and self.c[1] == "lambda":
            if debug: print(">>>> DESUGAR LAMBDA >>>>")
            name = eatLambda(self.c)
            var = eatExpression(self.c)
            if len(self.c) == 1: self.c = self.c[0]
            if var[0] == "[":
                var.pop(0)
                var.pop()
            lam = JLambda(name, var, self.c)
            self.c = lam
            if debug: print("self.c=", self.c)
    def step(self, cnt):
        if isinstance(self.c, list) and self.c[1] == "if":
            if debug: print(">>>> RULE 1 >>>>")
            eatBracket(self.c)    # remove if
            ec = eatExpression(self.c)
            et = eatExpression(self.c)
            ef = eatExpression(self.c)
            self.k = kif(self.env, et, ef, self.k)
            self.c = ec
        elif isinstance(self.k, kapp) and isinstance(self.c, JLambda):
            if debug: print(">>>> RULE LAMBDA >>>>")
            clo = closure(self.c, self.env)
            clo.env[self.c.name] = copy.deepcopy(clo)
            self.c = clo
            self.env = dict()
        elif isinstance(self.k, kapp) and not self.k.lExpr and self.k.lVal and isinstance(self.k.lVal[-1], closure) and (isinstance(self.c, int) or isinstance(self.c, JLambda) or isinstance(self.c, closure)):
            if debug: print(">>>> RULE CLOSURE >>>>")
            clo = self.k.lVal[-1]
            num = substituteList(clo.env, self.c)
            self.env = clo.env
            self.k.lVal.insert(0, self.c)
            name = clo.lam.name
            for var in reversed(clo.lam.lVar):
                self.env[var] = self.k.lVal.pop(0)
            self.env[name] = copy.deepcopy(clo)
            eb = clo.lam.eBody
            if isinstance(eb, list) and len(eb) > 1:
                if eb[1] == "lambda":
                    eb.pop(0)
                    eb.pop()
                    eb = desugar(eb)
                if isinstance(eb, list) and eb[0] != "[":
                    eb.insert(0, "[")
                    eb.append("]")
            self.c = eb
            self.k = self.k.frame
            self.k.env = dict()
        elif isinstance(self.c, list) and (self.c[1] in primAll or isFunction(self.c[1]) or isinstance(self.c[1], JLambda) or isinstance(self.c[1], closure) or self.c[1] == "["):
            if debug: print(">>>> RULE 4 >>>>")
            if self.c[1] == "[":
                self.c.pop(0)
                self.c.pop()
                c = eatExpression(self.c)
            else:
                c = eatBracket(self.c)
            self.k = kapp([], self.env, self.c, self.k)
            self.c = c
        elif isinstance(self.k, kif) and bool(self.c) == False:
            if debug: print(">>>> RULE 2 >>>>")
            self.c = self.k.eFalse
            self.env = self.k.env
            self.k = self.k.frame
        elif isinstance(self.k, kif) and bool(self.c) == True:
            if debug: print(">>>> RULE 3 >>>>")
            self.c = self.k.eTrue
            self.env = self.k.env
            self.k = self.k.frame
#        elif (isinstance(self.c, str) and self.c.islower()) or (isinstance(self.c, list) and self.c[1] in self.env and self.c[1].isupper()):
        elif (isinstance(self.c, str) and self.c.islower()) or (isinstance(self.c, list) and self.c[1] in self.env):
            if debug: print(">>>> RULE 8 >>>>")
            expr = self.c if isinstance(self.c, list) else [self.c]
            cnt = substituteList(self.env, expr)
            if cnt == 0: print(">>>>>>>>>> ERROR no substitutions?? >>>>>>>>>>>>>>>>>>>>>>>>")
            se = expr if isinstance(self.c, list) else expr.pop()
            self.c = se
            self.env = dict()
        elif isinstance(self.k, kapp) and self.k.lExpr:
            if debug: print(">>>> RULE 5 >>>>")
            self.env = self.k.env
            self.k.lVal.insert(0, self.c)
            var = eatExpression(self.k.lExpr)
            if isinstance(var, list) and len(var) == 3: var = var[1]
            self.c = var
        elif isinstance(self.k, kapp) and not self.k.lExpr and self.k.lVal[-1] in primAll:
            if debug: print(">>>> RULE 6 >>>>")
            self.k.lVal.insert(0, self.c)
            n = list(reversed(self.k.lVal))
            j1 = desugar(n)
            self.c = j1.interp()
            self.env = dict()
            self.k = self.k.frame
        elif isinstance(self.k, kapp) and not self.k.lExpr and isFunction(self.k.lVal[-1]):
            if debug: print(">>>> RULE 7 >>>>")
            varList, expr = getFunction(self.k.lVal[-1])
            self.k.lVal.insert(0, self.c)
            n = list(reversed(self.k.lVal))
            n.pop(0)    # remove func name
            if len(n) != len(varList): sys.exit("incorrect number of args passed to function?")
            envDict = dict(zip(varList, n))
#            substituteList(envDict, expr)
#            if debug: print(">>>>", "AFTER", expr)
            self.c = flatten(expr)
            self.env = envDict
            self.k = self.k.frame
        else:
            sys.exit("can't step no more??")

def interpCEK(se):
    se = eatDefinitions(se)
    st = cek0(se)
    cnt = 0
    print("inject")
    print("    ", st, "<<<<", "st" + str(cnt))
    while(True):
#        if cnt > 11: sys.exit("too many!!!")
        if isinstance(st.k, kret) and isinstance(st.c, int):
            break
        if isinstance(st.c, str) and st.c.islower() and not st.env:
            break
        cnt += 1
        if debug: st.dump()
        st.desugar()
        st.step(cnt)
        print("    ", st, "<<<<", "st" + str(cnt))
    print("extract")
    print("ans=", st.c)
    return st.c

se1 = []
se1.append([[["lambda", ["n"], ["if", ["=", "n", 1], 1, ["*", "n", ["rec", ["-", "n", 1]]]]], 6], 720])

print()
print("="*80)
print(">"*8, "task 37: Extend desugar to allow not mentioning the recursive name, as well as provide a default")
print("="*80)


for l in se1:
    print()
    print("="*80)
    print("="*80)
    print(l)
    debug = 1
    clearDict()
    CEKCheck(l[0], l[1])
