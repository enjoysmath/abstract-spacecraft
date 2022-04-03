from core.qt_tools import Pen, simple_max_contrasting_color, set_pen_style, set_pen_color
from PyQt5.QtGui import QPainterPath, QColor
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtWidgets import QGraphicsObject, QMenu
from graphics.containable import Containable
import stringcase
from graphics.text import Text
from dialog.color_dialog import ColorDialog

class GraphicsShape(QGraphicsObject):
    def __init__(self):
        QGraphicsObject.__init__(self)
        self._pen = Pen(Qt.magenta, 2.0)   # TODO: DEBUG, changing pen width overlaps selection shape
        self._paintPath = QPainterPath()
        self._selectionPath = QPainterPath()
        self._boundingRect = QRectF()
        self._selectionPen = Pen(Qt.black, 1.0, Qt.DotLine)
        self._bboxPad = 4.0
        self._contentPad = 8.0
        self._penColorDialog = ColorDialog(f'Set {self.__class__.__name__.lower()} pen color')
        self._penColorDialog.setCurrentColor(Qt.magenta)
        self._penColorDialog.currentColorChanged.connect(self.set_pen_color)
        
    def _setState(self, data:dict):
        #self.setParentItem(data['parent'])
        self._pen = data['pen']
        self._selectionPen = data['selection pen']
        self._bboxPad = data['bbox pad']
        self.setVisible(data['visible'])
        self.setPos(data['pos'])
        self.update()
        
    def _getState(self, data:dict):
        #data['parent'] = self.parentItem()
        data['pen'] = self._pen
        data['selection pen'] = self._selectionPen
        data['bbox pad'] = self._bboxPad
        data['visible'] = self.isVisible()
        data['pos'] = self.pos()
        return data
                    
    @property
    def pen(self):
        return self._pen
    
    def setPen(self, pen:Pen):
        if pen != self._pen:
            self._pen = pen
            if pen.color() != self._penColorDialog.currentColor():
                self._penColorDialog.setCurrentColor(pen.color())
            self.update()
    
    def paint_shape(self):
        return self._paintPath
    
    def shape_box(self):        
        children = self.childItems()
        shapeBox = QRectF()
        p = self._contentPad
        for c in children:
            if isinstance(c, Containable) and c.contained_in_bbox:
                if isinstance(c, GraphicsShape):
                    shapeBox = shapeBox.united(c.shape_box().translated(c.pos()))        
                elif isinstance(c, Text):
                    shapeBox = shapeBox.united(c.boundingRect().translated(c.pos()))
        return shapeBox.adjusted(-p, -p, p, p)
    
    def _updatePaintPath(self):
        self._paintPath.clear()
        p = self._bboxPad
        self._paintPath.addRect(self.shape_box())
        
    def _updateBoundingRect(self):
        raise NotImplementedError
    
    def _updateSelectionPath(self):
        self._selectionPath.clear()
        p = (self._bboxPad + self.pen.widthF()) / 2.0
        self._selectionPath.addRect(self._bbox.adjusted(-p, -p, p, p))
        
    def paint(self, painter, option, widget):
        if self.isSelected() and self.scene():
            pen = self._selectionPen
            pen.setColor(simple_max_contrasting_color(self.scene().backgroundBrush().color()))
            painter.setPen(pen)
            painter.drawPath(self._selectionPath)
        
    def build_context_menu(self, menu:QMenu, sep=False):
        if sep:
            menu.addSeparator()
        menu.addAction('Pen color').triggered.connect(self.show_pen_color_change_dialog)
        menu1 = menu.addMenu('Pen style')
        currentStyle = self.pen.style()
        
        for styleStr in ('SolidLine', 'DashLine', 'DotLine', 'DashDotLine', 'DashDotDotLine'):
            style = eval('Qt.' + styleStr)
            action = menu1.addAction(stringcase.capitalcase(styleStr))
            action.setCheckable(True)
            action.toggled.connect(lambda b, style=style: self.setPen(set_pen_style(self.pen, style)))
            if currentStyle == style:
                action.setChecked(True)        
        return menu
    
    def show_pen_color_change_dialog(self):
        self._penColorDialog.exec_()    
    
    def set_pen_color(self, color):
        if self._pen.color() != color:
            self.setPen(set_pen_color(self._pen, color))
            self._penColorDialog.setCurrentColor(color)
            
