from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEvent

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        self.setSpacing(spacing)
        self.itemList = []
        
    def __setstate__(self, data):
        self.__init__()
        self.setSpacing(data['spacing'])
        for widget in data['widgets']:
            self.addWidget(widget)
            
    def __getstate__(self):
        return {
            'spacing' : self.spacing(),
            'widgets' : [self.itemAt(k).widget() for k in range(self.count())],
        }
    
    def __deepcopy__(self, memo):
        copy = type(self)()
        memo[id(self)] = copy
        copy.setSpacing(self.spacing())
        copy.setMargin(self._margin)
        for k in range(self.count()):
            copy.addWidget(deepcopy(self.itemAt(k).widget(), memo))
        return copy        
    
    def __del__(self):
        self.clear()
        
    def clear(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
            
        return size

    def _doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal)

            spaceY = self.spacing() + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, 
                QtWidgets.QSizePolicy.PushButton, 
                QtCore.Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
    
    def removeWidget(self, widget):
        for k in range(len(self.itemList)):
            item = self.itemList[k]
            if item.widget() is widget:
                self.itemList.pop(k)
                break
        else:
            assert(0)
        super().removeWidget(widget)
        widget.setParent(None)  #BUGFIX: required
        self.setGeometry(self.geometry())
        widget.removeEventFilter(self)
        
    def addWidget(self, widget):
        widget.installEventFilter(self)
        super().addWidget(widget)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Wheel:
            event.accept()
            return True
        return super().eventFilter(watched, event)
    

if __name__ == '__main__':

    import sys

    class Window(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()

            flowLayout = FlowLayout()
            widget = QtWidgets.QWidget()
            flowLayout.addWidget(QtWidgets.QPushButton("Short"))
            flowLayout.addWidget(QtWidgets.QPushButton("Longer"))
            flowLayout.addWidget(QtWidgets.QPushButton("Different text"))
            flowLayout.addWidget(QtWidgets.QPushButton("More text"))
            flowLayout.addWidget(QtWidgets.QPushButton("Even longer button text"))
            widget.setLayout(flowLayout)
            self.setCentralWidget(widget)

            self.setWindowTitle("Flow Layout")

    core.app = QtWidgets.QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit(core.app.exec_())