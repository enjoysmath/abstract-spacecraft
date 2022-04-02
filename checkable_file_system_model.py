from PyQt5.QtCore import Qt, pyqtSignal, QDirIterator, QDir
from PyQt5.QtWidgets import QFileSystemModel
import os

class CheckableFileSystemModel(QFileSystemModel):
    check_state_changed = pyqtSignal(str, bool)
    
    def __init__(self):
        super().__init__()
        self.checkStates = {}
        self.rowsInserted.connect(self.checkAdded)
        self.rowsRemoved.connect(self.checkParent)
        self.rowsAboutToBeRemoved.connect(self.checkRemoved)

    def checkState(self, index):
        return self.checkStates.get(self.filePath(index), Qt.Unchecked)

    def setCheckState(self, index, state, emitStateChange=True):
        path = self.filePath(index)
        if self.checkStates.get(path) == state:
            return
        self.checkStates[path] = state
        if emitStateChange:
            self.check_state_changed.emit(path, bool(state))

    def checkAdded(self, parent, first, last):
        # if a file/directory is added, ensure it follows the parent state as long
        # as the parent is already tracked; note that this happens also when 
        # expanding a directory that has not been previously loaded
        if not parent.isValid():
            return
        if self.filePath(parent) in self.checkStates:
            state = self.checkState(parent)
            for row in range(first, last + 1):
                index = self.index(row, 0, parent)
                path = self.filePath(index)
                if path not in self.checkStates:
                    self.checkStates[path] = state
        self.checkParent(parent)

    def checkRemoved(self, parent, first, last):
        # remove items from the internal dictionary when a file is deleted; 
        # note that this *has* to happen *before* the model actually updates, 
        # that's the reason this function is connected to rowsAboutToBeRemoved
        for row in range(first, last + 1):
            path = self.filePath(self.index(row, 0, parent))
            if path in self.checkStates:
                self.checkStates.pop(path)

    def checkParent(self, parent):
        # verify the state of the parent according to the children states
        if not parent.isValid():
            return
        childStates = [self.checkState(self.index(r, 0, parent)) for r in range(self.rowCount(parent))]
        newState = Qt.Checked if all(childStates) else Qt.Unchecked
        oldState = self.checkState(parent)
        if newState != oldState:
            self.setCheckState(parent, newState)
            self.dataChanged.emit(parent, parent)
        self.checkParent(parent.parent())

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsUserCheckable

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return super().data(index, role)

    def setData(self, index, value, role, checkParent=True, emitStateChange=True):
        if role == Qt.CheckStateRole and index.column() == 0:
            self.setCheckState(index, value, emitStateChange)
            for row in range(self.rowCount(index)):
                # set the data for the children, but do not emit the state change, 
                # and don't check the parent state (to avoid recursion)
                self.setData(index.child(row, 0), value, Qt.CheckStateRole, 
                             checkParent=False, emitStateChange=False)
            self.dataChanged.emit(index, index)
            if checkParent:
                self.checkParent(index.parent())
            return True

        return super().setData(index, value, role)
    
    def list_all_checked_filenames(self, root=None):
        if root is None:
            root = self.rootPath()
            
        iterator = QDirIterator(root, QDir.Files, QDirIterator.Subdirectories)
        
        while iterator.hasNext():
            yield iterator.next()                       


if __name__ == '__main__':
    class Test(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            layout = QtWidgets.QVBoxLayout(self)
    
            self.tree = QtWidgets.QTreeView()
            layout.addWidget(self.tree, stretch=2)
    
            model = CheckableFileSystemModel()
            model.setRootPath('')
            self.tree.setModel(model)
            self.tree.setSortingEnabled(True)
            self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
            self.logger = QtWidgets.QPlainTextEdit()
            layout.addWidget(self.logger, stretch=1)
            self.logger.setReadOnly(True)
    
            model.check_state_changed.connect(self.updateLog)
            self.resize(640, 480)
            QtCore.QTimer.singleShot(0, lambda: self.tree.expand(model.index(0, 0)))
    
        def updateLog(self, path, checked):
            if checked:
                text = 'Path "{}" has been checked'
            else:
                text = 'Path "{}" has been unchecked'
            self.logger.appendPlainText(text.format(path))
            self.logger.verticalScrollBar().setValue(
                self.logger.verticalScrollBar().maximum())
            
    import sys
    app = QtWidgets.QApplication(sys.argv)
    test = Test()
    test.show()
    sys.exit(app.exec_())