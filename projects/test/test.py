import vip

class A:
    def __init__(self, p, q):
        self.p = p
        self.q = q

class B:
    def __init__(self, r, s):
        self.r = r
        self.s = s

class C:
    def __init__(self, t, u):
        self.t = t
        self.u = u
        
    def ftn(self, p, q):
        return self
        
def D(p, q):
    return p

server = vip.VIP()

server.addClassFromFile(int, "templates/number.jinja")
server.addClassFromFile(float, "templates/number.jinja")
server.addClassFromFile(str, "templates/string.jinja")

server.addClassFromFile(A, "templates/A.jinja")
server.addClassFromFile(B, "templates/B.jinja")
server.addClassFromFile(C, "templates/C.jinja")


a1 = A(1, "hi")
a2 = A(2, a1)
a3 = A(3, "hello")

b1 = B(a1, a2)
b2 = B(4, 5)
b3 = B(None, b1)

c1 = C("hi", "yay")

b3.r = c1

server.addFunctionFromFile(D, "templates/D.jinja")
server.addFunctionFromFile(C.ftn, "templates/C.ftn.jinja")

server.addInstance(D)

server.addInstance(a1)
server.addInstance(a2)
server.addInstance(a3)
server.addInstance(b1)
server.addInstance(b2)
server.addInstance(b3)
t = server.addInstance(c1)


server.run()