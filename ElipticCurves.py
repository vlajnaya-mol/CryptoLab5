import random
from GF import generate_gf_class
from point import generate_point_class
from hashlib import sha256


class ElipticCurve:
    def __init__(self, m, f, A, B, n, Ld):
        self.Ln = n.bit_length()
        
        assert Ld % 16 == 0 and Ld >= 2 * self.Ln, "bad Ld"
        
        self.m, self.f, self.n, self.Ld = m, f, n, Ld
        self.GF = generate_gf_class(m, f)
        self.A, self.B = self.GF(A), self.GF(B)
        self.Point = generate_point_class(self.GF, self.A, self.B)
        self.ZERO, self.ONE = self.GF(0), self.GF(1)
        self.O = self.Point(self.ZERO, self.ZERO)
        self.max_rand = (1 << (self.Ln - 1)) - 1
        
        self.P = self.gen_base_point()
        self.hash_func = lambda T: int.from_bytes(sha256(T).digest(), "big")
        
    def gen_base_point(self):
        P = self.random_point()
        while P.mul(self.n) != self.O or P == self.O or not self.point_on_curve(P):
            P = self.random_point()
        return P
    
    def random_num(self, lo=1, hi=None):
        if hi is None:
            hi = self.max_rand
        return random.randint(lo, hi)
    
    def random_point(self):
        return self.Point.random()

    def point_on_curve(self, p):
        return (p.y.pow(2) + p.x * p.y) == (p.x.pow(3) + self.A * p.x.pow(2) + self.B)

    def presign(self):
        Fe = self.ZERO
        while Fe == self.ZERO:
            e = self.random_num()
            R = self.P.mul(e)
            Fe = R.x
        return Fe, e
    
    def gen_private_k(self):
        return self.random_num(lo=1)
    
    def gen_public_k(self, d):
        return -self.P.mul(d)
    
    def sign(self, T, d):
        assert type(T) == bytes 
        
        h = self.GF(self.hash_func(T))
        
        if h == self.ZERO:
            h = self.ONE
            
        s = r = 0
        while s == 0:
            while r == 0:
                Fe, e = self.presign()
                y = h * Fe
                y.value = y.value & self.max_rand
                r = y.value
            s = (e + d*r) % self.n
        D = ElipticCurve.concat_to_signature(r, s, self.Ld)
        return T, D

    def check_signature(self, T, D, Q):
        assert type(T) == bytes 
        
        h = self.GF(self.hash_func(T))
        
        if h == self.ZERO:
            h = self.ONE
            
        r, s = ElipticCurve.split_signature(D, self.Ld)

        if not 0 < r < self.n or not 0 < s < self.n:
            return False

        R = self.P.mul(s) + Q.mul(r)
        y = h * R.x 
        y.value = y.value & self.max_rand
        r_hat = self.GF.to_int(y, self.Ln)
        return r_hat == r

    @staticmethod
    def concat_to_signature(r, s, Ld):
        return (s << (Ld // 2)) + r
    
    @staticmethod
    def split_signature(D, Ld):
        return D & ((1 << (Ld // 2)) - 1), D >> (Ld // 2)