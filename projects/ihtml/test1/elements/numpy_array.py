import ihtml

class ArrayWrap(ihtml.Element):
    def __init__(self, array):
        super().__init__("./numpy.array.jinja")
        self.array = array
    
    def 