import random


def generate_gf_class(m, f):
    max_gf = 1 << m


    class ConcreteGF:
        def __init__(self, number):
            self.value = number & (max_gf - 1) if number > max_gf else number

        def __add__(self, other):
            return ConcreteGF(self.value ^ other.value)

        def __mul__(self, other):
            a, b = self.value, other.value
            mask = max_gf - 1
            p = 0
            while a and b:
                if b & 1:
                    p ^= a
                b >>= 1
                carry = a >> (m - 1)
                a = (a << 1) & mask
                if carry:
                    a ^= mask & f
            return ConcreteGF(p)

        def __pow__(self, other):
            return ConcreteGF(self.pow(other.value).value) 

        def __eq__(self, other):
            return self.value == other.value

        def __ne__(self, other):
            return not self == other

        def __truediv__(self, other):
            return self * other.inverse()

        def __repr__(self):
            return str(self.value)

        def pow(self, exp):
            result = ConcreteGF(1)
            base = self
            while exp > 0:
                if exp % 2:
                    result = result * base
                exp //= 2
                base = base * base
            return result

        def sqrt(self):
            return self.pow(max_gf // 2)

        def trace(self):
            t = self
            two = ConcreteGF(2)
            for _ in range(1, m):
                t = t ** two + self
            return t

        def half_trace(self):
            t = self
            for _ in range(1, (m + 1) // 2):
                t = t.pow(4) + self
            return t

        def inverse(self):
            return self.pow(max_gf - 2)
        
        @staticmethod
        def solve(u, w):
            if u == ZERO:
                return w.sqrt(), 1
            if w == ZERO:
                return ZERO, 2
            v = w * u.inverse() ** TWO
            if v.trace() == ONE:
                return ZERO, 0
            return v.half_trace() * u, 2
        
        @staticmethod
        def random():
            return ConcreteGF(random.randint(0, f - 1))
        
        @staticmethod
        def to_int(gf_number, Ln):
            return gf_number.value & ((1 << (Ln - 1)) - 1)
    
    ZERO, ONE, TWO, THREE = ConcreteGF(0), ConcreteGF(1), ConcreteGF(2), ConcreteGF(3)
    return ConcreteGF