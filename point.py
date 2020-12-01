import random


def generate_point_class(GF, A, B):
    ZERO, ONE, TWO, THREE = GF(0), GF(1), GF(2), GF(3)
    
    
    class ConcretePoint:
        def __init__(self, x, y):
            self.x, self.y = x, y
        
        def __add__(self, other):
            if other == O:
                return self

            if self == O:
                return other

            if self.x == other.x and other.y == self.x + self.y:
                return O
            
            if self == other:
                return self.double()
            
            l = (self.y + other.y) / (self.x + other.x)
            x = l ** TWO + l + self.x + other.x + A
            y = l * (self.x + x) + x + self.y
            return ConcretePoint(x, y)
        
        def __eq__(self, other):
            return self.x == other.x and self.y == other.y

        def __neg__(self):
            return ConcretePoint(self.x, self.x + self.y)

        def __repr__(self):
            return f"({self.x}, {self.y})"
        
        def double(self):
            if self.x == ZERO:
                return O
            
            mu = self.x + self.y / self.x
            x = mu ** TWO + mu + A
            y = self.x ** TWO + (mu + ONE) * x
            return ConcretePoint(x, y)

        def mul(self, n_times):
            res = O
            term = self
            while n_times:
                if n_times % 2:
                    res += term
                term += term
                n_times >>= 1
            return res
        
        @staticmethod
        def random():
            k = 0
            while k == 0:
                u = GF.random()
                w = u.pow(3) + A * u.pow(2) + B
                z, k = GF.solve(u, w)
            return ConcretePoint(u, z)
    
    O = ConcretePoint(ZERO, ZERO)
    return ConcretePoint