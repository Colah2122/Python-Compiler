
from abc import ABC, abstractmethod

debug = 1

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

j0 = []
j0.append([JNum(9), 9])
j0.append([JPlus(JNum(2),JNum(3)), 5])
j0.append([JMult(JNum(2),JNum(7)), 14])
j0.append([JPlus(JNum(1),JMult(JNum(2),JNum(5))), 11])
j0.append([JPlus(JNum(-3),JMult(JNum(-1),JNum(9))), -12])
j0.append([JPlus(JNum(-114),JPlus(JNum(1),JMult(JNum(-2),JNum(-5)))), -103])
j0.append([JMult(JNum(14),JPlus(JNum(1),JPlus(JNum(2),JNum(5)))), 112])
j0.append([JPlus(JNum(3),JPlus(JNum(2),JPlus( JMult(JNum(3),JNum(4)),JMult(JNum(-1),JNum(4))))), 13])
j0.append([JPlus(JNum(5),JPlus(JNum(1),JMult(JNum(2),JMult(JNum(7),JNum(5))))), 76])
j0.append([JPlus(JMult(JNum(2),JNum(3)),JPlus(JPlus(JPlus(JNum(2),JNum(-4)),JNum(2)),JMult(JNum(2),JNum(3)))), 12])
j0.append([JMult(JPlus(JNum(1),JMult(JNum(2),JNum(5))),JMult(JNum(14),JPlus(JNum(1),JPlus(JNum(2),JNum(5))))), 1232])
j0.append([JPlus(JMult(JNum(2),JNum(3)),JPlus(JPlus(JPlus(JPlus(JNum(-3),JMult(JNum(-1),JNum(9))),JNum(-4)),JNum(2)),JMult(JNum(2),JNum(3)))), -2])


print()
print("="*80)
print(">"*8, "task 3: ", "Write a test-suite of a dozen J0 programs.")
print("="*80)
for e in j0:
    print(e[0].ppt(), " >>> ", e[1], "???")
