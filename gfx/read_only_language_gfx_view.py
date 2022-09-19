from gfx.language_gfx_view import LanguageGfxView
from gfx.language_canvas import LanguageCanvas

class ReadOnlyLanguageGfxView(LanguageGfxView):
   def __init__(self, canvas:LanguageCanvas):
      super().__init__(canvas)
      self.fit_contents_in_view()
      self.setMinimumHeight(0)
      self.setMinimumWidth(0)      
      
   def mousePressEvent(self, event):
      event.accept()
      
   def mouseReleaseEvent(self, event):
      event.accept()
      
   def contextMenuEvent(self, event):
      event.accept()
      
   def mouseDoubleClickEvent(self, event):
      event.accept()
      
   
      