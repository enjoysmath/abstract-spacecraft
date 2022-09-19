from PyQt5.QtWidgets import QWidget, QApplication
import gfx.logical_rule_view as rule_view
from ui.ui_proof_view import Ui_ProofView
from gfx.proof_step import ProofStep

class ProofView(QWidget, Ui_ProofView):
   def __init__(self, statement:rule_view.LogicalRuleView, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self._proofSteps = []
      self._statement = statement
      self.statementButton.clicked.connect(self.navigate_to_statement)
      self.addProofStepButton.clicked.connect(self.add_proof_step)
      self._proofStepLink = None
   
   def __setstate__(self, data):
      self.__init__()
      self._statement = data['statement']
      self._proofSteps = data['proof steps']
      
   @property
   def statement(self):
      return self._statement
   
   def navigate_to_statement(self):
      if self._statement is not None:
         window = self._statement.window()
         window.set_current_language_view(self._statement)
      
   def add_proof_step(self, proof_step:ProofStep=None):
      if proof_step is None:
         app = QApplication.instance()
         app.set_link_requester(self)
         return
      
      self._proofSteps.append(proof_step)
      self.proofStepLayout.addWidget(proof_step)
      proof_step.remove_requested.connect(lambda: self.remove_proof_step(proof_step))
      
   def set_link(self, link):
      self.add_proof_step(ProofStep(link))
      
   def remove_proof_step(self, proof_step:ProofStep):
      self.proofStepLayout.removeWidget(proof_step)
      self._proofSteps.remove(proof_step)
      proof_step.remove_requested.disconnect()
      