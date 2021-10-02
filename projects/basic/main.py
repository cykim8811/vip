import vip
import debugger


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

server.addFunctionFromFile(createNumber.create, 'templates/class/createNumber/create.jinja')
server.addClassFromFile(createNumber, 'templates/class/createNumber/self.jinja')
toolbar.add(createNumber())

server.addFunctionFromFile(createString.create, 'templates/class/createString/create.jinja')
server.addClassFromFile(createString, 'templates/class/createString/self.jinja')
toolbar.add(createString())

def add(p, q): return p + q
def substract(p, q): return p - q
def multiply(p, q): return p * q
def divide(p, q): return p / q
def mod(p, q): return p % q
def power(p, q): return p ** q
server.addFunctionFromFile(add, 'templates/function/add.jinja')
server.addFunctionFromFile(substract, 'templates/function/substract.jinja')
server.addFunctionFromFile(multiply, 'templates/function/multiply.jinja')
server.addFunctionFromFile(divide, 'templates/function/divide.jinja')
server.addFunctionFromFile(mod, 'templates/function/mod.jinja')
server.addFunctionFromFile(power, 'templates/function/power.jinja')
toolbar.add(add)
toolbar.add(substract)
toolbar.add(multiply)
toolbar.add(divide)
toolbar.add(mod)
toolbar.add(power)


server.addClassFromFile(Toolbar, 'templates/class/toolbar.jinja')
server.addInstance(toolbar)

# debugger.debug(server.workspace.memory)

server.run()