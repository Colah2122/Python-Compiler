from abc import ABC, abstractmethod
import sys
import copy

debug = 1
primJApp = ("+", "*", "/", "-", "<=", "<", "=", ">", ">=")
primAll = primJApp + ("pair", "inl", "inr", "fst", "snd")
num = 0

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
        if self.prim not in primJApp: sys.exit(self.prim + " not supported?")
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

class JPair(JExpr):
    def __init__(self, lVar, rVar):
        self.lVar = lVar
        self.rVar = rVar
        if not isinstance(lVar, JExpr): sys.exit("lVar must be a JExpr?")
        if not isinstance(rVar, JExpr): sys.exit("rVar must be a JExpr?")
    def __str__(self):
        return "pair(" + str(self.lVar) + "," + str(self.rVar) + ")"
    def interp(self):
        return copy.deepcopy(self)

class JVariant(JExpr):
    def __init__(self, name, pair):
        self.name = name
        self.pair = pair
        if not isinstance(name, str): sys.exit("name must be a string?")
        if not isinstance(pair, JPair) and pair != "unit": sys.exit("pair must be a JPair?")
    def __str__(self):
        return self.name + "." + str(self.pair)
    def interp(self):
        return copy.deepcopy(self)

class JCase(JExpr):
    def __init__(self, name, xl, el, xr, er):
        if not isinstance(name, str): sys.exit("variant must be a string?")
        if not isinstance(xl, str): sys.exit("xl must be a string?")
        if not isinstance(el, list) and not isinstance(el, str) and not isinstance(el, int): sys.exit("el must be a list, string or int?")
        if not isinstance(xr, str): sys.exit("xr must be a string?")
        if not isinstance(er, list) and not isinstance(er, str) and not isinstance(er, int): sys.exit("er must be a list, string or int?")
        self.name = name
        self.xl = xl
        self.el = copy.deepcopy(el)
        self.xr = xr
        self.er = copy.deepcopy(er)
    def __str__(self):
        return "case " + self.name + " [" + self.xl + "=>" + myStr(self.el) + "] [" + self.xr + "=>" + myStr(self.er) + "]"
    def interp(self):
        sys.exit("never9")

def isJValue(expr):
    if isinstance(expr, int): return True
    if isinstance(expr, JVariant): return True
    if isinstance(expr, JPair): return True
    if isinstance(expr, str) and expr == "unit": return True
    return False

def isCEKValue(expr):
    if isinstance(expr, JPair): return True
    if isinstance(expr, JVariant): return True
    if isinstance(expr, JLambda): return True
    if isinstance(expr, closure): return True
    return False

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
        num = arg
        cnt2 = substitute1(num, var, expr)
        if debug and cnt2 > 0: print("PUT", num, "-->", var, "INTO", orig)
        cnt += cnt2
    return cnt

def CEKCheck(e, expAns):
    actAns = interpCEK(e)
    isCorrect = str(actAns) == str(expAns)
    result = "CORRECT!!" if isCorrect else "FAILURE!!"
    print(actAns, " = ", expAns, " >>> ", result)
    return isCorrect

def desugar(se):
    if isinstance(se, int):
        return JNum(se)
    if isinstance(se, JExpr):
        return se
    if isinstance(se, str) and se == "unit":
        return se
    if isinstance(se, list):
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
        elif myLen == 3 and mySym in "pair":
            return JPair(desugar(se[1]), desugar(se[2]))
        elif myLen == 2 and mySym[0:2] in "in":
            return JVariant(mySym, desugar(se[1]))
        elif myLen == 2 and mySym in "fst":
            return se[1].lVar
        elif myLen == 2 and mySym in "snd":
            return se[1].rVar
        elif myLen == 3 and mySym in primJApp:
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
    lam = eatBracket(l)    # remove lambda
    if lam != "lambda": sys.exit("lambda is missing??")
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
        self.stdlib = {}
        self.stdlib["empty"] = flatten(["inl", "unit"])
        self.stdlib["cons"] = closure(JLambda("cons", ["data", "rest"], flatten(["inr", ["pair", "data", "rest"]])), {})
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
        if isinstance(self.c, list) and self.c[0] == "[" and self.c[1] == "let":
            if debug: print(">>>> DESUGAR LET >>>>")
            let = eatBracket(self.c)    # remove let
            if let != "let": sys.exit("let is missing??")
            var1 = []
            ec = []
            while True:
                if self.c[0] == "in": break
                se = eatExpression(self.c)
                print("se=",se)
                v = eatBracket(se)
                var1.append(v)
                if se[0] != "[":
                    ec.append(se[0])
                elif se[1] == "lambda":
                    name2 = eatLambda(se)
                    var2 = eatExpression(se)
                    var2.pop(0)
                    var2.pop()
                    lam2 = JLambda(name2, var2, se)
                    ec.append(lam2)
                else:
                    ec.append(se)
            print("var1=",var1)
            print("ec=",ec)
            i = self.c.pop(0)    # remove in
            if i != "in": sys.exit("cant find let in??")
            print("eb=",self.c)
            print("self.env=",self.env)
            print("myself.c=",self.c)
            lam = JLambda("rec", var1, self.c)
            ec.insert(0, lam)
            ec.insert(0, "[")
            ec.append("]")
            self.c = ec
            if debug: print("self.c=", self.c)
        elif isinstance(self.c, list) and self.c[0] == "[" and self.c[1] == "lambda":
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
        elif isinstance(self.c, list) and self.c[0] == "[" and self.c[1] == "case":
            if debug: print(">>>> DESUGAR CASE >>>>")
            eatBracket(self.c)    # remove case
            var = self.c.pop(0)
            print("var=",var)
            inl = eatExpression(self.c)
            xl = eatBracket(inl)
            print("xl=",xl)
            el = eatExpression(inl)
            print("el=",el)
            inr = eatExpression(self.c)
            xr = eatBracket(inr)
            print("xr=",xr)
            er = eatExpression(inr)
            print("er=",er)
            case = JCase(var, xl, el, xr, er)
            self.c = case
            if debug: print("self.c=", self.c)
            print("type(self.c)=", type(self.c))
    def step(self, cnt):
        if isinstance(self.c, list) and self.c[0] == "[" and self.c[1] == "if":
            if debug: print(">>>> RULE 1 >>>>")
            eatBracket(self.c)    # remove if
            ec = eatExpression(self.c)
            et = eatExpression(self.c)
            ef = eatExpression(self.c)
            self.k = kif(self.env, et, ef, self.k)
            self.c = ec
        elif isinstance(self.k, kapp) and isinstance(self.c, JLambda):
            if debug: print(">>>> RULE LAMBDA >>>>")
            print("self.env=",self.env)
            clo = closure(self.c, self.env)
            clo.env[self.c.name] = copy.deepcopy(clo)
            print("clo.env=",clo.env)
            self.c = clo
            self.env = dict()
        elif isinstance(self.c, JCase):
            if debug: print(">>>> RULE CASE >>>>")
            var = self.env[self.c.name]
            print("var=",var)
            inlr = var.name
            print("inlr=",inlr)
            eb = self.c.er if inlr == "inr" else self.c.el
            print("eb=",eb)
            x = self.c.xr if inlr == "inr" else self.c.xl
            print("x=",x)
            env = {}
            env[x] = var.pair
            print("env=",env)
            num = substituteList(env, eb)
            print("eb=",eb)
            self.c = eb
        elif isinstance(self.k, kapp) and not self.k.lExpr and self.k.lVal and isinstance(self.k.lVal[-1], closure) and (isCEKValue(self.c) or isinstance(self.c, int)):
            if debug: print(">>>> RULE CLOSURE >>>>")
            clo = self.k.lVal[-1]
            print("clo=",clo)
            num = substituteList(clo.env, self.c)
            print("num=",num)
            print("self.c=",self.c)
            print("self.env=",self.env)
            self.env = clo.env
            print("clo.env=",clo.env)
            print("self.k.lVal=",self.k.lVal)
            if num > 0 and isinstance(self.c, list):
                eatBracket(self.c)    # remove function
                while True:
                    e = eatExpression(self.c)
                    if isinstance(e, list) and len(e) == 0: break
                    print("e=",e)
                    self.k.lVal.insert(0, e)
            else:
                self.k.lVal.insert(0, self.c)
            name = clo.lam.name
            print("clo.lam.lVar=",clo.lam.lVar)
            print("self.k.lVal=",self.k.lVal)
            if len(clo.lam.lVar) != len(self.k.lVal)-1: sys.exit("num vars != vals??")
            for var in reversed(clo.lam.lVar):
                self.env[var] = self.k.lVal.pop(0)
                print(var,"<<<<<<<",self.env[var])
            self.env[name] = copy.deepcopy(clo)
            eb = copy.deepcopy(clo.lam.eBody)
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
            print("self.c=",self.c)
            print("self.k=",self.k)
            print("self.env=",self.env)
        elif isinstance(self.c, list) and self.c[0] == "[" and (self.c[1] in primAll or isCEKValue(self.c[1]) or self.c[1] == "["):
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
        elif (isinstance(self.c, str) and (self.c in self.env or self.c in self.stdlib)) or (isinstance(self.c, list) and self.c[0] == "[" and (self.c[1] in self.env or self.c[1] in self.stdlib)) or (isinstance(self.c,list) and (self.c[0] in self.env or self.c[0] in self.stdlib)):
            if debug: print(">>>> RULE 8 >>>>")
            expr = self.c if isinstance(self.c, list) else [self.c]
            self.env.update(self.stdlib)
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
        elif isinstance(self.k, kapp) and not self.k.lExpr and self.k.lVal and self.k.lVal[-1] in primAll:
            if debug: print(">>>> RULE 6 >>>>")
            self.k.lVal.insert(0, self.c)
            n = list(reversed(self.k.lVal))
            j1 = desugar(n)
            print("j1=",j1)
            self.c = j1.interp()
            self.env = dict()
            self.k = self.k.frame
        else:
            sys.exit("can't step no more??")

def interpCEK(se):
    st = cek0(se)
    cnt = 0
    print("inject")
    print("    ", st, "<<<<", "st" + str(cnt))
    while True:
#        if cnt > 350: sys.exit("too many!!!")
        if isinstance(st.k, kret) and isJValue(st.c):
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
se1.append([["let", ["x", 8], "in", ["let", ["y", 7], "in", ["+", "x", "y"]]], 15])
se1.append([["let", ["x", ["+", 1, 7]], "in", ["let", ["y", ["-", 9, 2]], "in", ["+", "x", "y"]]], 15])
se1.append([["let", ["x", 8], "in", ["let", ["x", ["+", "x", 1]], "in", ["+", "x", "x"]]], 18])
se1.append([[["lambda", "Repeat", ["i", "sum"], ["if", ["<", "i", 3], "i", "sum"]], 4, 6], 6])
se1.append([["let", ["l", 5], "in", [["lambda", "R", ["i", "s"], ["if", ["<", "i", "l"], "i", "s"]], 4, 6]], 4])
se1.append([[["lambda", "Fsum", ["n"], ["if", ["=", "n", 1], 1, ["+", "n", ["Fsum", ["-", "n", 1]]]]], 6], 21])

se1.append([[["lambda", "R", ["i", "s"], ["if", ["<", "i", 5], ["R", ["+", "i", 1], ["+", "i", "s"]], "s"]], 0, 0], 10])
se1.append([[["lambda", "Factorial", ["n"], ["if", ["=", "n", 1], 1, ["*", "n", ["Factorial", ["-", "n", 1]]]]], 6], 720])
se1.append([["let", ["F", ["lambda", ["x"], ["+", "x", 2]]],
             "in", ["F", ["F", ["F", ["F", 3]]]]], 11])
se1.append([[["lambda", "rec", ["x"], ["+", "x", 2]], 3], 5])
se1.append([["let", ["F", ["lambda", "rec", ["x"], ["+", "x", 2]]],
             "in", ["F", 3]], 5])
se1.append([["let", ["F", ["lambda", ["n"], ["+", "n", 3]]],
                    ["x", ["+", 4, 5]],
                    ["y", 7],
             "in", ["F", ["+", "x", "y"]]], 19])
se1.append([["let", ["F", ["lambda", ["x"], ["+", "x", 2]]],
             "in", ["let", ["G", ["lambda", ["x", "y"], ["+", ["F", "x"], ["F", "y"]]]],
                    "in", ["G", ["+", 1, 2], 4]]], 11])
se1.append([["let", ["F", ["lambda", ["x"], ["+", "x", 2]]],
             "in", ["F", 3]], 5])
se1.append([["let", ["Simple", ["lambda", ["n"], ["+", ["*", "n", 3], 4]]],
             "in", ["Simple", 3]], 13])
se1.append([["let", ["Simple", ["lambda", ["a", "b", "c", "d", "e", "f", "g", "h"], ["+", "a", "b", "c", "d", "e", "f", "g", "h"]]],
             "in", ["Simple", 1, 2, 3, 4, 5, 6, 7, 8]], 36])
se1.append([["let", ["Plus1", ["lambda", ["n"], ["+", "n", 1]]],
                    ["Plus2", ["lambda", ["n"], ["+", "n", 2]]],
                    ["Plus3", ["lambda", ["n"], ["+", "n", 3]]],
                    ["Plus4", ["lambda", ["n"], ["+", "n", 4]]],
                    ["Plus5", ["lambda", ["n"], ["+", "n", 5]]],
             "in", ["+", ["Plus1", 5], ["Plus2", 4], ["Plus3", 3], ["Plus4", 2], ["Plus5", 1]]], 30])
se1.append([["let", ["Plus1", ["lambda", ["n"], ["+", "n", 1]]],
                    ["Plus2", ["lambda", ["n"], ["+", "n", 2]]],
                    ["Plus3", ["lambda", ["n"], ["+", "n", 3]]],
                    ["Plus4", ["lambda", ["n"], ["+", "n", 4]]],
                    ["Plus5", ["lambda", ["n"], ["+", "n", 5]]],
             "in", ["+", ["Plus1", ["Plus2", ["Plus3", ["Plus4", ["Plus5", 1]]]]], 12]], 28])
se1.append([["let", ["Double", ["lambda", ["x"], ["+", "x", "x"]]],
             "in", ["let", ["Quad", ["lambda", ["y"], ["Double", ["Double", "y"]]]],
                    "in", ["Quad", ["+", 1, ["Double", 3]]]]], 28])
se1.append([["let", ["Double", ["lambda", ["x"], ["+", "x", "x"]]],
             "in", ["Double", ["Double", 1]]], 4])
se1.append([["let", ["Factorial", ["lambda", "iFac", ["n"], ["if", ["=", "n", 1], 1, ["*", "n", ["iFac", ["-", "n", 1]]]]]],
             "in", ["+", 1, ["Factorial", 6]]], 721])
se1.append([["let", ["ImN", ["lambda", ["n"], ["+", "n", 0]]],
             "in", ["+", ["ImN", 4], ["ImN", 3], ["ImN", -3], ["ImN", 6]]], 10])
se1.append([["let", ["Sum1toN", ["lambda", "iSum", ["n"], ["if", ["=", "n", 1], 1, ["+", "n", ["iSum", ["+", "n", -1]]]]]],
             "in", ["+", 1, ["Sum1toN", 5]]], 16])
se1.append([["let", ["FibN", ["lambda", ["n"], ["if", ["=", "n", 0], 0, ["if", ["=", "n", 1], 1, ["+", ["rec", ["-", "n", 1]], ["rec", ["-", "n", 2]]]]]]],
             "in", ["FibN", 5]], 5])
se1.append([["let", ["last", 5],
             "in", ["let", ["DoTimes", ["lambda", "iRep", ["i", "sum"], ["if", ["<", "i", "last"], ["iRep", ["+", "i", 1], ["+", "i", "sum"]], "sum"]]],
                    "in", ["DoTimes", 0, 0]]], 10])
se1.append(["unit", "unit"])
se1.append([["pair", 5, 6], "pair(5,6)"])
se1.append([["pair", 5, ["pair", 6, 7]], "pair(5,pair(6,7))"])
se1.append([["pair", ["pair", 2, 3], ["pair", 6, 7]], "pair(pair(2,3),pair(6,7))"])
se1.append([["let", ["p", ["pair", 5, 6]], "in", ["fst", "p"]], 5])
se1.append([["let", ["p", ["pair", 3, ["pair", 5, 6]]], "in", ["snd", ["snd", "p"]]], 6])
se1.append([["let", ["p", ["pair", ["pair", ["pair", 1, 2], ["pair", 3, 4]], ["pair", ["pair", 5, 6], ["pair", 7, 8]]]],
             "in", ["snd", ["snd", "p"]]], "pair(7,8)"])
se1.append([["let", ["p", ["pair", ["pair", ["pair", 1, 2], ["pair", 3, 4]], ["pair", ["pair", 5, 6], ["pair", 7, 8]]]],
             "in", ["fst", ["fst", "p"]]], "pair(1,2)"])
se1.append([["let", ["p", ["pair", ["pair", ["pair", 1, 2], ["pair", 3, 4]], ["pair", ["pair", 5, 6], ["pair", 7, 8]]]],
             "in", ["fst", "p"]], "pair(pair(1,2),pair(3,4))"])
se1.append([["let", ["p1", ["pair", 7, 8]],
             "in", ["let", ["p2", ["pair", 9, "p1"]],
                    "in", ["snd", "p2"]]], "pair(7,8)"])
se1.append([["let", ["p1", ["pair", 7, 8]],
             "in", ["let", ["p2", ["pair", 9, "p1"]],
                    "in", ["fst", "p2"]]], 9])
se1.append([["let", ["p", ["pair", 3, ["pair", 5, ["pair", 6, ["pair", 8, ["pair", 10, 12]]]]]],
             "in", ["snd", ["snd", ["snd", ["snd", "p"]]]]], "pair(10,12)"])
se1.append([["cons", 2, "empty"], "inr.pair(2,inl.unit)"])
se1.append([["cons", 1, ["cons", 2, "empty"]], "inr.pair(1,inr.pair(2,inl.unit))"])
se1.append([["cons", ["cons", ["cons", ["cons", 1, 2], 3], 4], 5], "inr.pair(inr.pair(inr.pair(inr.pair(1,2),3),4),5)"])
se1.append([["let", ["list", ["cons", 6, ["cons", 7, ["cons", 8, ["cons", 9, "empty"]]]]],
                    ["length", ["lambda", "rec2", ["l"], ["case", "l", ["_", 0], ["p", ["+", 1, ["rec2", ["snd", "p"]]]]]]],
             "in", ["length", "empty"]], 0])
se1.append([["let", ["list", ["cons", 6, ["cons", 7, ["cons", 8, ["cons", 9, "empty"]]]]],
                    ["length", ["lambda", "rec2", ["l"], ["case", "l", ["_", 0], ["p", ["+", 1, ["rec2", ["snd", "p"]]]]]]],
             "in", ["length", "list"]], 4])
se1.append([["let", ["list", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["add2", ["lambda", "rec1", ["x"], ["+", "x", 2]]],
                    ["map", ["lambda", "rec3", ["F", "l"], ["case", "l", ["_", "l"], ["p", ["cons", ["F", ["fst", "p"]], ["rec3", "F", ["snd", "p"]]]]]]],
             "in", ["map", "add2", "list"]], "inr.pair(3,inr.pair(4,inr.pair(5,inl.unit)))"])
se1.append([["let", ["list", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["add", ["lambda", "rec1", ["x", "y"], ["+", "x", "y"]]],
                   ["reduce", ["lambda", "rec3", ["F", "z", "l"], ["case", "l", ["_", "z"], ["p", ["rec3", "F", ["F", "z", ["fst", "p"]], ["snd", "p"]]]]]],
             "in", ["reduce", "add", 0, "list"]], 6])
se1.append([["let", ["a", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["b", ["cons", 4, ["cons", 5, ["cons", 6, "empty"]]]],
                    ["append", ["lambda", "rec3", ["x", "y"], ["case", "x", ["_", "y"], ["p", ["cons", ["fst", "p"], ["rec3", ["snd", "p"], "y"]]]]]],
             "in", ["append", "a", "b"]], "inr.pair(1,inr.pair(2,inr.pair(3,inr.pair(4,inr.pair(5,inr.pair(6,inl.unit))))))"])
se1.append([["let", ["a", ["cons", 1, ["cons", 2, "empty"]]],
                    ["b", ["cons", 4, "empty"]],
                    ["c", ["cons", 6, "empty"]],
                    ["append", ["lambda", "rec3", ["x", "y"], ["case", "x", ["_", "y"], ["p", ["cons", ["fst", "p"], ["rec3", ["snd", "p"], "y"]]]]]],
             "in", ["append", "c", ["append", "a", "b"]]], "inr.pair(6,inr.pair(1,inr.pair(2,inr.pair(4,inl.unit))))"])
se1.append([["let", ["list", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["add2", ["lambda", "rec1", ["x"], ["+", "x", 2]]],
                    ["map", ["lambda", "rec3", ["F", "l"], ["case", "l", ["_", "l"], ["p", ["cons", ["F", ["fst", "p"]], ["rec3", "F", ["snd", "p"]]]]]]],
             "in", ["map", "add2", ["map", "add2", "list"]]], "inr.pair(5,inr.pair(6,inr.pair(7,inl.unit)))"])
se1.append([["let", ["a", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["b", ["cons", 4, ["cons", 5, ["cons", 6, "empty"]]]],
                    ["append", ["lambda", "rec3", ["x", "y"], ["case", "x", ["_", "y"], ["p", ["cons", ["fst", "p"], ["rec3", ["snd", "p"], "y"]]]]]],
                    ["length", ["lambda", "rec2", ["l"], ["case", "l", ["_", 0], ["p", ["+", 1, ["rec2", ["snd", "p"]]]]]]],
             "in", ["length", ["append", "a", "b"]]], 6])
se1.append([["let", ["a", ["cons", 1, ["cons", 2, ["cons", 3, "empty"]]]],
                    ["b", ["cons", 4, ["cons", 5, ["cons", 6, "empty"]]]],
                    ["append", ["lambda", "rec3", ["x", "y"], ["case", "x", ["_", "y"], ["p", ["cons", ["fst", "p"], ["rec3", ["snd", "p"], "y"]]]]]],
                    ["add2", ["lambda", "rec1", ["x"], ["+", "x", 2]]],
                    ["map", ["lambda", "rec3", ["F", "l"], ["case", "l", ["_", "l"], ["p", ["cons", ["F", ["fst", "p"]], ["rec3", "F", ["snd", "p"]]]]]]],
             "in", ["map", "add2", ["append", "a", "b"]]], "inr.pair(3,inr.pair(4,inr.pair(5,inr.pair(6,inr.pair(7,inr.pair(8,inl.unit))))))"])

print()
print("="*80)
print(">"*8, "task 44: Extend your J4 data structures to J5 and extend the CEK2 machine to CEK3 to evaluate J5.")
print("="*80)

for l in se1:
    print()
    print("="*80)
    print("="*80)
    print(l)
    debug = 1
    CEKCheck(l[0], l[1])
