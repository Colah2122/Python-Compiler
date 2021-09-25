
from abc import ABC, abstractmethod

class JExpr(ABC):
    def ppt(self):
        return self.__str__();
    @abstractmethod
    def __str__(self):
        pass

class JNum(JExpr):
    def __init__(self, eNum):
        self.eNum = int(eNum)
    def __str__(self):
        return str(self.eNum)

class JPlus(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight
    def __str__(self):
        return "(+ " + str(self.eLeft) + " " + str(self.eRight) + ")"

class JMult(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight
    def __str__(self):
        return "(* " + str(self.eLeft) + " " + str(self.eRight) + ")"


print()
print("="*80)
print(">"*8, "task 2: Write a pretty-printer for J0 programs")
print("="*80)

a = JNum(3)
b = JPlus(JNum(3),JNum(5))
c = JMult(JNum(-3),JNum(-2))
d = JPlus(JMult(JNum(-4),JNum(5)),JMult(JNum(2),JNum(12)))

print("a=",a.ppt())
print("b=",b.ppt())
print("c=",c.ppt())
print("d=",d.ppt())
