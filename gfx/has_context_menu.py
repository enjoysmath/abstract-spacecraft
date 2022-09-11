from PyQt5.QtWidgets import QMenu

Action, SubMenu, ToggleAction = range(3)

class HasContextMenu:   
    context_menus = {
        
    }
    
    def __init__(self):
        pass
        
        
    def contextMenuEvent(self, event):
        menu = self.build_context_menu()
        if menu:
            menu.exec_(event.screenPos())
        
    def build_context_menu(self, menu=None):
        if menu is None:
            menu = QMenu()
            
        Type = type(self)
        if Type in self.context_menus:
            context = self.context_menus[Type]
            
            for title, data in context:
                
                if data['action kind'] == Action:
                    action = menu.addAction(title)
                    action.triggered.connect()
            
        
    
    
    

