from ui.ui_debug_watch_widget import Ui_DebugWatchWidget
from PyQt5.QtWidgets import QWidget, QGraphicsEllipseItem, QGraphicsPathItem, QGridLayout
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QColor
from PyQt5.QtCore import QRectF, pyqtSignal
from core.qt_tools import css_color, generate_random_color
from widget.line_edit import LineEdit
import math

class DebugWatchWidget(QWidget, Ui_DebugWatchWidget):
    pause_debug_requested = pyqtSignal()
    play_debug_requested = pyqtSignal()
    
    point_size = 1
    line_size = 1   
    float_precision = 3
    
    def __init__(self, item):
        super().__init__()
        super().__init__()
        self.setupUi(self)
        self._watched = item
        self.python_id_line.setText(str(hex(id(item)).upper()))
        # We can just do:
        if hasattr(item, 'objectName'):
            self.object_name_line.setText(item.objectName())
        else:
            self.object_name_line.setEnabled(False)
        
        self.position_line = LineEdit() 
        self.bounding_rect_line = LineEdit()
        self.trans_origin_line = LineEdit()
        
        self.geom_line_spots = [self.position_line_spot, self.bounding_rect_line_spot,
                 self.trans_origin_line_spot, None]
        self.geom_line_edits = [self.position_line, self.bounding_rect_line, 
                                self.trans_origin_line, None]
        self.geom_checks = [self.position_check, self.bounding_rect_check, 
                            self.trans_origin_check, self.shape_check]
        
        d = self.point_size
        rect = QRectF(-d/2, -d/2, d, d)
        self._shape = QGraphicsPathItem(item.mapToScene(item.shape()))
        self._rect = QGraphicsPathItem()
        self._transOrigin = QGraphicsEllipseItem(rect)
        self._position = QGraphicsEllipseItem(rect)
                        
        self.geometries = [self._position, self._rect, self._transOrigin, self._shape]
        self.setup()
        
    def setup(self):
        pens = [QPen(generate_random_color(), self.line_size) for k in range(4)]
        brushes = [pen.color() for pen in pens] 
        
        for k in range(len(self.geom_checks)):
            check = self.geom_checks[k]
            line_edit = self.geom_line_edits[k]
            if line_edit is not None:
                line_edit.editingFinished.connect(self.play_debug_requested.emit)
                line_edit.editing_started.connect(self.pause_debug_requested.emit)     
                spot = self.geom_line_spots[k]
                spot.setLayout(QGridLayout())
                spot.layout().addWidget(line_edit)
            geom = self.geometries[k]
            geom.setZValue(-math.inf)  # This is required, Idk how else other than really large value
            geom.setBrush(brushes[k])
            geom.setPen(pens[k])
            self._watched.scene().addItem(geom)
            geom.setVisible(check.isChecked())
            check.toggled.connect(geom.setVisible)
            check.setStyleSheet(css_color(pens[k].color()))
            
        self.update_debug_fields()
            
    def update_debug_fields(self):
        item = self._watched
        self.position_line.setText(self.format_point(item.scenePos()))
        self.bounding_rect_line.setText(self.format_rect(item.boundingRect()))
        self.trans_origin_line.setText(self.format_point(item.transformOriginPoint()))
        # BUGFIX: use scenePos() not map to scene because we override it
        self._position.setPos(item.scenePos())   
        self._transOrigin.setPos(item.mapToScene(item.transformOriginPoint()))
        path = QPainterPath()
        path.addPolygon(item.mapToScene(item.boundingRect()))
        self._rect.setPath(path)
        self._shape.setPath(item.mapToScene(item.shape()))
    
    @staticmethod
    def formatf(flt):       
        cls = DebugWatchWidget
        return ('%.' + str(cls.float_precision) + 'f') % (flt)
    
    @staticmethod
    def format_point(point):
        cls = DebugWatchWidget
        return cls.formatf(point.x()) + ', ' + cls.formatf(point.y())
    
    @staticmethod
    def format_rect(rect):
        cls = DebugWatchWidget
        return cls.formatf(rect.x()) + ', ' + \
               cls.formatf(rect.y()) + ', ' + \
               cls.formatf(rect.width()) + ', ' + \
               cls.formatf(rect.height()) 
        
    def watched_item(self):
        return self._watched