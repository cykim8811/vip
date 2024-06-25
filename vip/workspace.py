from jinja2 import Template


none_template = """
<span class='vipnone {{vip.register()}}'>None</span>
"""

default_template = """
<div style='display: inline-block; height: 24px; background-color: rgb(150, 150, 150);
border-radius: 5px; border: 1px solid black; user-select: none;'
class='{{vip.register()}}'>
{{ str(instance.__class__.__name__) }}<br>
{{ instance }}</div>
"""

textbox_template = """
<span class='input editable {{classText}}' role='textbox' contenteditable style='{{styleText}}' onblur='updateVariableBuiltin(this, this.innerText);'>{{instance}}</span>
"""

errormessage_template = """
<div class='viperror {{vip.register()}} draggable'>
Error: {{instance}}
</div>
"""


class VIPTemplate:
    def __init__(self, instancewrap, workspace):
        self.workspace = workspace
        self.instanceId = instancewrap.id
        self.instancewrap = instancewrap
        self.memberbox_template = Template("<span class='vipmember {{ instanceId }}.{{ member }}'>{{ data|safe }}</span>")
        self.textbox_template = Template(textbox_template)
    
    def member(self, member):
        value = None
        if member not in self.instancewrap.target.__dict__:
            self.instancewrap.target.__dict__[member] = None
        var = self.instancewrap.target
        value = var.__dict__[member]
            
        search = [t for t in self.workspace.memory if t.target is value]
        if len(search) == 0:
            tempinstancewrap = self.workspace.addInstance(value, display=False)
            return self.memberbox_template.render(data=tempinstancewrap.render(), member=member, instanceId=self.instanceId)
        else:
            instancewrap = search[0]
            return self.memberbox_template.render(data=instancewrap.render(), member=member, instanceId=self.instanceId)
    
    def item(self, index):
        value = self.instancewrap.target[index]
        search = [t for t in self.workspace.memory if t.target is value]
        if len(search) == 0:
            tempinstancewrap = self.workspace.addInstance(value, display=False)
            return self.memberbox_template.render(data=tempinstancewrap.render(), member="["+str(index)+"]", instanceId=self.instanceId)
        else:
            instancewrap = search[0]
            return self.memberbox_template.render(data=instancewrap.render(), member="["+str(index)+"]", instanceId=self.instanceId)
    
    def argument(self, member):
        if member not in self.instancewrap.target.__dict__:
#             tempinstancewrap = InstanceWrap(self.workspace, var.__dict__[member], classwrap=self.workspace.none_classwrap, display=False)
#             return self.memberbox_template.render(data=tempinstancewrap.render(), member=member, instanceId=self.instanceId)
            pass
        return self.member(member)

    def method(self, methodName):
        method = self.instancewrap.classwrap.target.__dict__[methodName]
        search = [t for t in self.workspace.memory if type(t.target) is FunctionManager and t.target.target is method]
        if len(search) == 0:
            pass  # TODO: handle this
        else:
            search[0].target.isMethod = True
            return search[0].render()
    
    def textbox(self, member=None, classText="", styleText="display: inline-block; font-size: 1em; margin: 1px; min-width: 12px; background-color: white; border-radius: 5px; border: 1px solid black;"):
        if member is None:
            pass
        innerText = self.textbox_template.render(classText=classText, styleText=styleText, instance=self.instancewrap.target.__dict__[member])
        return self.memberbox_template.render(instanceId=self.instanceId, member=member, data=innerText)
        
    def register(self):
        return "vipinstance vipinstance" + str(self.instanceId)

class ClassWrap:
    lastId = 200000000
    def __init__(self, targetClass, template):
        self.target = targetClass
        self.template = Template(template)
        
        ClassWrap.lastId += 1
        self.id = ClassWrap.lastId

class InstanceWrap:
    lastId = 100000000
    def __init__(self, workspace, targetInstance, classwrap=None, template=None, display=False):
        if classwrap is None and template is None: raise
        # classwrap==None: function
        # classwrap!=None: normal instance
        self.target = targetInstance
        self.classwrap = classwrap
        self.template = classwrap.template if classwrap else template
        InstanceWrap.lastId += 1
        self.id = InstanceWrap.lastId
        self.workspace = workspace
        self.display = display
    
    def render(self):
        return self.template.render(instance=self.target, vip=VIPTemplate(self, self.workspace))
        
        
class FunctionManager:
    def __init__(self, targetFunction, isMethod=False):
        self.target = targetFunction
        self.args = {}
        self.isMethod = isMethod
    
    def call(self):
        try:
            args = []
            kwargs = {}
            for a in self.args:
                if not self.isMethod and a == "self": continue
                if type(a) is int:
                    while a+1 > len(args): args.push(None)
                    args[a] = self.args[a]
                else:
                    kwargs[a] = self.args[a]
            return self.target(**kwargs);
        except Exception as e:
            return ExceptionMessage(str(e))

class ExceptionMessage:
    def __init__(self, msg):
        self.msg = msg;
    def __str__(self):
        return self.msg
        
class Workspace:
    def __init__(self):
        self.class_wrap_list = []
        self.memory = []
        
        self.sendCallback = None
        
        self.default_classwrap = ClassWrap(None, default_template)
        self.none_classwrap = ClassWrap(None, none_template)
        self.memory.append(InstanceWrap(self, None, self.none_classwrap, display=False));
        
        self.addClass(ExceptionMessage, errormessage_template)
        self.env = Template('').environment
        self.env.globals.update(globals()['__builtins__'])
        
    
    def registerCallback(self, callback):
        self.sendCallback = callback
    
    def addClass(self, _class, template):
        search = [t for t in self.class_wrap_list if t.target == _class]
        if len(search) > 0:
            return None # Class already registered
        classwrap = ClassWrap(_class, template)
        self.class_wrap_list.append(classwrap)
        return classwrap
    
    def addClassFromFile(self, _class, template_path):
        with open(template_path, 'r') as f:
            self.addClass(_class, f.read())
        
    def addInstance(self, _instance, display=True):
        searchinst = [t for t in self.memory
                      if ((t.target is _instance) or (((type(t.target) is FunctionManager) and (t.target.target is _instance))))]
        if len(searchinst) != 0 and type(_instance) not in [str, int, float, complex, tuple]:
            searchinst[0].display=display
            return searchinst[0]
        search = [t for t in self.class_wrap_list if t.target == type(_instance)]
        if len(search) > 0:
            classwrap = search[0]
            instancewrap = InstanceWrap(self, _instance, classwrap, display=display)
            self.memory.append(instancewrap)
            return instancewrap
        else:
            instancewrap = InstanceWrap(self, _instance, self.default_classwrap, display=display)
            self.memory.append(instancewrap)
            return instancewrap

    def addFunction(self, _function, template, display=True):
        search = [t for t in self.memory if t.target is _function]
        for t in search:
            t.target = FunctionManager(t.target)
            t.target.template = Template(template)
            t.target.classwrap = None
            return t
        instancewrap = InstanceWrap(self, FunctionManager(_function), template=Template(template), display=display)
        self.memory.append(instancewrap)
        return instancewrap
    
    def addFunctionFromFile(self, _function, template_path, display=False):
        with open(template_path, 'r') as f:
            self.addFunction(_function, f.read(), display=display)
    
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
            return [t.id for t in self.memory if t.display]
        if msg['type'] == "render":
            instancewrap = self.getInstanceById(msg['instanceId'])
            return instancewrap.render()
        if msg['type'] == "unmember":
            owner = msg['owner']
            member = msg['member']
            if '[' not in member:
                target = self.getInstanceById(owner)
                newId = self.addInstance(target.target.__dict__[member], display=False)
                if type(target.target) is FunctionManager:
                    target.target.__dict__[member] = None
                    target.target.args[member] = None
                    return newId.id
                target.target.__dict__[member] = None
                return newId.id
            else:
                index = member[member.find('[') + 1: -1]
                index = int(index) if index.isdigit() else index
                member = member[0: member.find('[')]
                target = self.getInstanceById(owner)
                if '__dict__' not in target.target:
                    newId = self.addInstance(target.target[index], display=False)
                    target.target[index] = None
                    return newId.id
                else:
                    newId = self.addInstance(target.target.__dict__[member][index], display=False)
                    if type(target.target) is FunctionManager:
                        target.target.args[member][index] = None
                    target.target.__dict__[member][index] = None
                    return newId.id
        if msg['type'] == "update_member_builtin":
            owner = msg['instanceId']
            member = msg['member']
            value = msg['value']
            target = self.getInstanceById(owner)
            if not owner:
                self.getInstanceById(member).target = value
            elif '[' not in member:
                if type(target.target) is FunctionManager:
                    target.target.args[member] = value
                    target.target.__dict__[member] = value
                else:
                    target.target.__dict__[member] = value
                    
            else:
                index = member[member.find('[') + 1: -1]
                index = int(index) if index.isdigit() else index
                member = member[0: member.find('[')]
                if owner:
                    if type(target.target) is FunctionManager:
                        target.target.args[member][index] = value
                    else:
                        target.target.__dict__[member][index] = value
                else:
                    self.getInstanceById(member).target[index] = value
                
        if msg['type'] == "update_member":
            owner = msg['owner']
            member = msg['member']
            instanceId = msg['instanceId']
            target = self.getInstanceById(owner)
            value = self.getInstanceById(instanceId)
            if '[' not in member:
                if type(target.target) is FunctionManager:
                    target.target.args[member] = self.getInstanceById(instanceId).target;
                if owner:
                    target.target.__dict__[member] = value.target
                else:
                    self.getInstanceById(member).target = value.target
            else:
                index = member[member.find('[') + 1: -1]
                index = int(index) if index.isdigit() else index
                member = member[0: member.find('[')]
                if type(target.target) is FunctionManager:
                    target.target.args[member][index] = self.getInstanceById(instanceId).target;
                if owner:
                    if '__dict__' not in target.target:
                        target.target[index] = value.target
                    else:
                        target.target.__dict__[member][index] = value.target
                else:
                    self.getInstanceById(member).target[index] = value.target
                
        if msg['type'] == "call":
            instanceId = msg['instanceId']
            target = self.getInstanceById(instanceId)
            result = target.target.call()
            return self.addInstance(result, display=True).id
    
    def send(self, data):
        self.sendCallback(data)