import vip
import numpy

class ndarrayWrap(vip.Element):
    def __init__(self, workspace, instance):
        # workspace: vip.Workspace that this vip.Element belongs to
        # instance : Python instance that this Wrapper is managing
        templatePath = os.path.dirname(os.path.abspath(__file__)) + "/array.jinja"
        with open(templatePath) as f:
            templateText = f.read()
            
        super().__init__(workspace, template)
        self.instance = instance
        
    # Callbacks
    def onTextboxEdit(self, classList, text):
        pass
    
    def onButtonClick(self, classList):
        # self.updateTemplate("<div></div")
        pass
    
    def onElementDrop(self, classList, element):
#         if 'p' in classList:
#             self.instance.p = element.instance
#             element.remove()
        pass