
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

e = []
e.append([JNum(9), 9])
e.append([JPlus(JNum(2),JNum(3)), 5])
e.append([JMult(JNum(2),JNum(7)), 14])
e.append([JPlus(JNum(1),JMult(JNum(2),JNum(5))), 11])
e.append([JPlus(JNum(-3),JMult(JNum(-1),JNum(9))), -12])
e.append([JPlus(JNum(-114),JPlus(JNum(1),JMult(JNum(-2),JNum(-5)))), -103])
e.append([JMult(JNum(14),JPlus(JNum(1),JPlus(JNum(2),JNum(5)))), 112])
e.append([JPlus(JNum(3),JPlus(JNum(2),JPlus( JMult(JNum(3),JNum(4)),JMult(JNum(-1),JNum(4))))), 13])
e.append([JPlus(JNum(5),JPlus(JNum(1),JMult(JNum(2),JMult(JNum(7),JNum(5))))), 76])
e.append([JPlus(JMult(JNum(2),JNum(3)),JPlus(JPlus(JPlus(JNum(2),JNum(-4)),JNum(2)),JMult(JNum(2),JNum(3)))), 12])
e.append([JMult(JPlus(JNum(1),JMult(JNum(2),JNum(5))),JMult(JNum(14),JPlus(JNum(1),JPlus(JNum(2),JNum(5))))), 1232])
e.append([JPlus(JMult(JNum(2),JNum(3)),JPlus(JPlus(JPlus(JPlus(JNum(-3),JMult(JNum(-1),JNum(9))),JNum(-4)),JNum(2)),JMult(JNum(2),JNum(3)))), -2])


print()
print("="*80)
print(">"*8, "task 3: Write a test-suite of a dozen J0 programs")
print("="*80)

for l in e:
    print("-"*50)
    print(l[0].ppt(), ">>>", l[1], "?????")
