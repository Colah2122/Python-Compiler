from abc import ABC, abstractmethod

class JExpr(ABC):
    pass

class JNum(JExpr):
    def __init__(self, eNum):
        self.eNum = int(eNum)

class JPlus(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight

class JMult(JExpr):
    def __init__(self, eLeft, eRight):
        self.eLeft = eLeft
        self.eRight = eRight


print()
print("="*80)
print(">"*8, "task 1: Define data structures to represent J0 programs")
print("="*80)

a = JNum(3)
b = JPlus(JNum(3),JNum(5))
c = JMult(JNum(-3),JNum(-2))
d = JPlus(JMult(JNum(-4),JNum(5)),JMult(JNum(2),JNum(12)))
