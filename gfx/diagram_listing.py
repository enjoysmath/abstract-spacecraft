from ui.ui_diagram_listing import Ui_DiagramListing
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
from gfx.language_canvas import LanguageCanvas
from gfx.language_gfx_view import LanguageGfxView
import _pickle as pickle
from gfx.language_listing import LanguageListing
from gfx.read_only_language_gfx_view import ReadOnlyLanguageGfxView

class DiagramListing(LanguageListing, Ui_DiagramListing):
   refresh_wait_interval_ms = 1500
   remove_requested = pyqtSignal()
   
   def __init__(self, diagram_view, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      scene_data = diagram_view.scene()
      self._sourceView = diagram_view
      self.diagramView = ReadOnlyLanguageGfxView(scene_data)
      self.layout().addWidget(self.diagramView, 1, 0, -1, -1)
      self.diagramTitleLabel.setText(diagram_view.tab_name)
      self._refreshTimer = None
      self.editButton.clicked.connect(self.navigate_to_diagram)
      self.removeButton.clicked.connect(self.remove_from_listing)
      
   def refresh_scene_data(self):
      if self._refreshTimer is None:
         self._refreshTimer = QTimer()
         self._refreshTimer.setSingleShot(True)
         self._refreshTimer.setInterval(self.refresh_wait_interval_ms)
         self._refreshTimer.timeout.connect(self._refreshSceneData)
         self._refreshTimer.start()
      
   def _refreshSceneData(self):
      self.diagramView.fit_contents_in_view()
      self._refreshTimer = None
      
   def navigate_to_diagram(self):
      if self._sourceView:
         self._sourceView.window().raise_()
         self._sourceView.window().set_current_language_view(self._sourceView)
         
   def remove_from_listing(self):
      self.remove_requested.emit()
      
   @property
   def source_view(self):
      return self._sourceView