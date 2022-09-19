from ui.ui_diagram_listing import Ui_DiagramListing
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication
from gfx.language_canvas import LanguageCanvas
from gfx.language_gfx_view import LanguageGfxView
import _pickle as pickle
from gfx.read_only_language_gfx_view import ReadOnlyLanguageGfxView

class DiagramListing(QWidget, Ui_DiagramListing):
   refresh_wait_interval_ms = 1500
   
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
      