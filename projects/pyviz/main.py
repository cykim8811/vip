import vip

server = vip.VIP()

server.addClassFromFile(str, 'templates/str.jinja')
server.addClassFromFile(int, 'templates/number.jinja')
server.addClassFromFile(float, 'templates/number.jinja')
server.addClassFromFile(dict, 'templates/dict.jinja')

server.addInstance("Hello, World!")
server.addInstance(42)
server.addInstance(3.14)
server.addInstance({"name": "John", "age": 42})


class A:
    def __init__(self):
        self.p = 3
        self.q = '4'

server.addClassFromFile(A, 'templates/A.jinja')
server.addInstance(A())

server.run()