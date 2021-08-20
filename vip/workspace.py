from jinja2 import Template


class ClassWrap:
    lastId = 0
    def __init__(self, targetClass, template):
        self.target = targetClass
        self.template = Template(template)
        
        self.id = ClassWrap.lastId
        ClassWrap.lastId += 1

class InstanceWrap:
    lastId = 0
    def __init__(self, targetInstance, classwrap=None, template=None):
        if classwrap is None and template is None: raise
        # classwrap==None: function
        # classwrap!=None: normal instance
        self.target = targetInstance
        self.classwrap = classwrap
        self.template = classwrap.template if classwrap else template  # Should be set right after creation
        self.id = InstanceWrap.lastId
        InstanceWrap.lastId += 1
    
    def render(self):
        return self.template.render(instance=self.target)
        
# class FunctionWrap:
#     def __init__(self, targetFunction, template):
#         self.target = targetFunction
#         self.template = template
        
class Workspace:
    def __init__(self):
        self.class_wrap_list = []
        self.memory = []
        
        self.sendCallback = None
    
    def registerCallback(self, callback):
        self.sendCallback = callback
    
    def addClass(self, _class, template):
        search = [t for t in self.class_wrap_list if t.target == type(_instance)]
        if len(search) > 0:
            return None # Class already registered
        classwrap = ClassWrap(_class, template)
        self.class_wrap_list.append(classwrap)
        return classwrap
    
    def addClassFromFile(self, _class, template_path):
        with open(template_path, 'r') as f:
            self.addClass(_class, f.read())
        
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
        search = [t for t in self.memory if t.target == _function]
        for i, t in enumerate(self.memory):
            if t.target == _function:
                t.template = Template(template)
                t.classwrap = None
                return t
        instancewrap = InstanceWrap(_instance, template=Template(template))
        self.memory.append(instancewrap)
        return instancewrap
    
    def addFunctionFromFile(self, _function, template_path):
        with open(template_path, 'r') as f:
            self.addFunction(_function, f.read())
    
    def getClassById(self, _id):  # Returns <ClassWrap>
        search = [t for t in self.class_wrap_list if t.id == _id]
        if len(search) == 0: return None
        return search[0]
    
    def getInstanceById(self, _id):  # Returns <InstanceWrap>
        search = [t for t in self.memory if t.id == _id]
        if len(search) == 0: return None
        return search[0]
    
    def getFunctionById(self, _id):  # Returns <FunctionWrap>
        search = [t for t in self.function_wrap_list if t.id == _id]
        if len(search) == 0: return None
        return search[0]
    
    def call(self, ftn, *args, **kwargs):
        try:
            ret = ftn(*args, **kwargs)
            if ret is None:
                return None
            else:
                return self.addInstance(self, ret)
        except:
            return None
        
    def removeInstance(self, _instance):
        for i, _inst in enumerate(self.memory):
            if _inst == _instance:
                del self.memory[i]
                return True
        return False
    
    def onMessage(self, msg):
        pass # if msg['type'] == ""
        
    def onRequest(self, msg):
        if msg['type'] == "memory":
            return [t.id for t in self.memory]
        if msg['type'] == "render":
            instanceWrap = self.getInstanceById(msg['instanceId'])
            return instanceWrap.render()
    
    def send(self, data):
        self.sendCallback(data)