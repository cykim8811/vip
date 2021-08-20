
class ClassWrap:
    lastId = 0
    def __init__(self, targetClass, template):
        self.target = targetClass
        self.template = template
        
        self.id = ClassWrap.lastId
        ClassWrap.lastId += 1

class InstanceWrap:
    lastId = 0
    def __init__(self, targetInstance, classwrap):
        self.target = targetInstance
        self.classwrap = classwrap
        
        self.id = InstanceWrap.lastId
        InstanceWrap.lastId += 1
        
class FunctionWrap:
    lastId = 0
    def __init__(self, targetFunction, template):
        self.target = targetFunction
        self.template = template
        
        self.id = FunctionWrap.lastId
        FunctionWrap.lastId += 1
        
class Workspace:
    def __init__(self):
        self.class_wrap_list = []
        self.memory = []
        self.function_wrap_list = []
    
    def addClass(self, _class, template):
        search = [t for t in self.class_wrap_list if t.target == type(_instance)]
        if len(search) > 0:
            return None # Class already registered
        classwrap = ClassWrap(_class, template)
        self.class_wrap_list.append(classwrap)
        return classwrap
        
    def addInstance(self, _instance):
        search = [t for t in self.class_wrap_list if t.target == type(_instance)]
        if len(search) > 0:
            classwrap = search[0]
            instancewrap = InstanceWrap(_instance, classwrap)
            self.memory.append(instancewrap)
            return instancewrap
        else:
            print("Exception: Cannot add instance before adding its class.")
            return None # Class Not Registered

    def addFunction(self, _function, template):
        search = [t for t in self.function_wrap_list if t.target == _function]
        if len(search) > 0:
            return None # Function already registered
        functionwrap = FunctionWrap(_function, template)
        self.function_wrap_list.append(functionwrap)
        return functionwrap
    
    def getClassById(self, _id):
        search = [t for t in self.class_wrap_list if t.id == _id]
        if len(search) == 0: return None
        return search[0]
    
    def getInstanceById(self, _id):
        search = [t for t in self.memory if t.id == _id]
        if len(search) == 0: return None
        return search[0]
    
    def getFunctionById(self, _id):
        search = [t for t in self.function_wrap_list if t.id == _id]
        if len(search) == 0: return None
        return search[0]