from ui.ui_proof_step import Ui_ProofStep
from gfx.language_listing import LanguageListing
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView
from gfx.logical_rule_listing import LogicalRuleListing
from gfx.diagram_listing import DiagramListing
from gfx.external_link_listing import ExternalLinkListing
from PyQt5.QtCore import pyqtSignal

class ProofStep(LanguageListing, Ui_ProofStep):
   remove_requested = pyqtSignal()
   
   def __init__(self, link, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self.removeAction.clicked.connect(self.remove_requested.emit)
      
      if isinstance(link, str):
         widget = ExternalLinkListing(link)
      elif isinstance(link, LanguageGfxView):
         widget = DiagramListing(link)
      elif isinstance(link, LogicalRuleView):
         widget = LogicalRuleListing(link)
         
      widget.remove_requested.connect(self.remove_requested.emit)
      self.layout().addWidget(widget, 0, 0, -1, 1)