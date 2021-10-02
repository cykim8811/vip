import vip
import numpy


server = vip.VIP()

server.addClassFromFile(int, 'templates/class/number.jinja')
server.addClassFromFile(float, 'templates/class/number.jinja')
server.addClassFromFile(str, 'templates/class/string.jinja')

class Toolbar:
    def __init__(self):
        self.functions = []
    
    def add(self, ftn):
        self.functions.append(ftn)
        
toolbar = Toolbar()


class createNumber:
    def __init__(self):
        self.data = 0
    def create(self):
        return int(self.data)

class createString:
    def __init__(self):
        self.data = "Hello World!"
    def create(self):
        return str(self.data)

class createArray:
    def __init__(self):
        self.width = 1
        self.height = 1
    def create(self):
        return numpy.zeros((int(self.width), int(self.height)))

server.addFunctionFromFile(createNumber.create, 'templates/class/createNumber/create.jinja')
server.addClassFromFile(createNumber, 'templates/class/createNumber/self.jinja')
toolbar.add(createNumber())

server.addFunctionFromFile(createString.create, 'templates/class/createString/create.jinja')
server.addClassFromFile(createString, 'templates/class/createString/self.jinja')
toolbar.add(createString())

server.addFunctionFromFile(createArray.create, 'templates/class/createArray/create.jinja')
server.addClassFromFile(createArray, 'templates/class/createArray/self.jinja')
toolbar.add(createArray())

def add(p, q): return p + q
def substract(p, q): return p - q
def multiply(p, q): return p * q
def matmul(p, q): return p @ q
server.addFunctionFromFile(add, 'templates/function/add.jinja')
server.addFunctionFromFile(substract, 'templates/function/substract.jinja')
server.addFunctionFromFile(multiply, 'templates/function/multiply.jinja')
server.addFunctionFromFile(matmul, 'templates/function/matmul.jinja')
toolbar.add(add)
toolbar.add(substract)
toolbar.add(multiply)
toolbar.add(matmul)

# numpy
server.addClassFromFile(numpy.ndarray, 'templates/class/numpy/array.jinja')


server.addClassFromFile(Toolbar, 'templates/class/toolbar.jinja')
server.addInstance(toolbar)


server.run()