from ui.ui_external_link_listing import Ui_ExternalLinkListing
from gfx.language_listing import LanguageListing
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

class ExternalLinkListing(LanguageListing, Ui_ExternalLinkListing):
   def __init__(self, link:str, link_text:str=None, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      if link_text is None:
         link_text = ''
      self._linkText = link_text
      self._baseLink = f'<a href="{link}">{link_text} 🔗</a>'
      self._link = link
      self.externalLinkLabel.setText(self._baseLink)
      self.removeButton.clicked.connect(self.remove_requested.emit)
      self.externalLinkLabel.linkActivated.connect(lambda url_str: QDesktopServices.openUrl(QUrl(url_str)))
      
   def set_link_text(self, text:str):
      self._linkText = text
      self.externalLinkLabel.setText(self._baseLink.replace('🔗', f'<a href="{self._link}">{text} 🔗</a>'))
      
   @property
   def source_view(self):
      return (self._link, self._linkText)