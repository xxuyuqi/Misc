import math

class Factor():
    def __init__(self,number):
        self.number = number
        if number >= 2 and self.isinteger(number):
            self.factorQuest()  
        

    def isinteger(self,number):
        if math.modf(number)[0] == 0.0:
            return True
        else :
            return False
    
    def factorQuest(self):
        factors = []
        for factor in range(1,math.ceil(math.sqrt(self.number))):
            if self.number % factor == 0:
                factors.extend([factor, self.number//factor])
        self.factors = sorted(factors,reverse=False)
        return None
    
    def isprime(self):
        if len(self.factors) == 2:
            return True
        else :
            return False


if __name__ == "__main__":
    '''
    QQ = []
    for i in range(10000,10000000000):
        session = Factor(i)
        if len(session.factors) >= 50:
            QQ.append(session.number)
        if i % 10000 == 0:
            print(i)
        del session
    print(QQ)
    '''
    session = Factor(136)
    print(len(session.factors))
    print(session.factors)                   
