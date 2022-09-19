from gfx.connectable import Connector, Connectable
from PyQt5.QtCore import pyqtSignal, Qt, QRectF, QLineF, QPointF, QTimer, QEvent
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsSceneMouseEvent, QMenu, QAction, QApplication
from PyQt5.QtGui import (QPainter, QPainterPath, QPolygonF, QPainterPathStroker, QColor,
                         QTransform, QVector2D)
from core.geom_tools import mag2D, dot2D, rect_to_poly, paint_selection_shape, closest_point_on_path
from math import acos, asin, atan2, pi, sin, cos, sqrt
from gfx.control_point import ControlPoint
import gfx.object
from core.qt_tools import Pen, set_pen_style, SimpleBrush, set_pen_color, set_pen_width
from copy import deepcopy
#from stringcase import camelcase
from gfx.text import Text
from gfx.graphics_shape import GraphicsShape
from gfx.bounded import Bounded
from gfx.drag_droppable import DragDroppable
from gfx.containable import Containable
from gfx.has_context_menu import HasContextMenu
from gfx.deletable import Deletable
from gfx.arrow_style import ArrowStyle
from gfx.object import Object
from gfx.linkable import Linkable

class Arrow(GraphicsShape, Connector, Bounded, DragDroppable, Containable, HasContextMenu, Deletable, Linkable):
    name_changed = pyqtSignal(str)
    bezier_toggled = pyqtSignal(bool)
    control_poitns_pos_changed = pyqtSignal(list)    # list of points
    end_point_double_clicked = pyqtSignal(ControlPoint, QPointF)
    mouse_pressed_end_point = pyqtSignal(ControlPoint, QPointF)
    mouse_released_end_point = pyqtSignal(ControlPoint, QPointF)
    
    source_was_set = pyqtSignal(Connectable)
    target_was_set = pyqtSignal(Connectable)
    
    SingleLine, DoubleLine, WavySingleLine, \
    WavyDoubleLine, TripleLine = range(5)
    
    NoHead, SingleHead, DoubleHead, TripleHead = range(4)    
    NoTail, HookTail, VeeTail = range(3)
    
    default_connect_pad = 10.0
    default_line_width = 1.5
    default_color = QColor(Qt.black)
    default_dotted_line = False
    default_relative_head_size = 5.0
    intersect_shape_width_multiple = 10.0    
    relative_control_point_size = 0.83
    control_point_edit_time = 2500
    
    def __init__(self, text:str=None, ctrl_points=None):
        self.is_initialized = False
        GraphicsShape.__init__(self)
        Connector.__init__(self)
        Bounded.__init__(self)
        DragDroppable.__init__(self)
        Containable.__init__(self)
        HasContextMenu.__init__(self)
        Deletable.__init__(self)
        Linkable.__init__(self)
        if text is not None:
            text = Text(text)
            text.setParentItem(self)      
        self._headPath = QPainterPath()
        self._linePath = QPainterPath()
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable | self.ItemIsSelectable | self.ItemSendsScenePositionChanges \
                      | self.ItemSendsGeometryChanges)
        self.setFlag(self.ItemIsMovable, False)
        #self.setFiltersChildEvents(True)
        self._contextMenu = None
        self._editTimer = None
        self._updatingPointPos = False
        self._updatingPoints = False  
        self._lastLabelPosLine = None
        self._lastPos = QPointF()
        self._intersectShape = None
        self.setZValue(1.0)
        self._shape = QPainterPath()        
        self._relativeHeadSize = self.default_relative_head_size      
        if ctrl_points is None:
            ctrl_points = [ControlPoint() for i in range(0, 4)]
        self._points = ctrl_points
        for point in self._points:
            point.setParentItem(self)
            #point.installSceneEventFilter(self)
        self._pointedness = 1.0
        self._bezier = None
        self._points[1].setVisible(False)
        self._points[2].setVisible(False)
        self._arrows = []
        self._tailStyle = self.NoTail
        self._headStyle = self.SingleHead
        self._lineCount = 2
        self._connectPad = self.default_connect_pad
        pen = set_pen_style(self.pen, Qt.DottedLine if self.default_dotted_line else Qt.SolidLine)
        pen = set_pen_color(pen, self.default_color)
        self._penColorDialog.currentColorChanged.connect(self.set_default_pen_color)
        pen = set_pen_width(pen, self.default_line_width)
        self._pen = pen
        for point in self._points:
            point.set_radius(self.relative_control_point_size * pen.widthF())        
        self.update_centroid_position()
        self._lastLabelPosLine = None 
        self.arrow_style = ArrowStyle()
        self.arrow_style.update_requested.connect(self.update)
        self.arrow_style.bezier_toggled.connect(self._toggleBezierControlPoints)
        self.update()
        self.is_initialized:bool = True
                        
    def __setstate__(self, data):
        self.__init__(ctrl_points=data['points'])
        GraphicsShape._setState(self, data['graphics shape'])
        Connector._setState(self, data['connector'])
        Containable._setState(self, data['containable'])
        Deletable._setState(self, data['deletable'])
        self._lastLabelPosLine = data['label pos line']
        self._connectPad = data['connect pad']
        if not self._bezier:
            self.set_line_points(self._points[0].pos(), self._points[-1].pos())
        for child in data['children']:
            child.setParentItem(self)
        #for p in self._points:
            #print(p.parentItem())
        
    def __getstate__(self):
        data = {
            'graphics shape' : GraphicsShape._getState(self, {}),
            'connector' : Connector._getState(self, {}),
            'containable' : Containable._getState(self, {}),
            'deletable' : Deletable._getState(self, {}),
            'points' : self._points,
        }
        #data["points"] = [point._getState({}) for point in self._points]
        data['connect pad'] = self._connectPad
        data['label pos line'] = self._lastLabelPosLine
        data['children'] = [child for child in self.childItems() if not isinstance(child, ControlPoint)]
        return data
    
    def post_init_setup(self):
        self.update()
        
    def set_updating_auto_layout(self, yes):
        self._updatingAutoLayout = yes
        
    def control_point_pos_change(self, pos):
        scene = self.scene()
        if scene:
            selected = scene.selectedItems()
            if len(selected) > 1 and self.isSelected():     # BUGFIX: Return in we're performing a multimove
                return
        self.update_ancestory_chain()
        
    def setPen(self, pen):
        for point in self._points:
            point.set_radius(self.relative_control_point_size * pen.widthF())
        self._pen = pen
   
    def set_head_style(self, style):
        if style != self._headStyle:
            string = 'self.' + style.replace(' ', '') + ('Head' if style != 'No Head' else '')
            self._headStyle = eval(string)
            self.update()
        
    def head_style(self):
        return self._headStyle
    
    def set_tail_style(self, style):
        if style != self._tailStyle:
            string = 'self.' + style.replace(' ', '') + ('Tail' if style != 'No Tail' else '')
            self._tailStyle = eval(string)
            self.update()
            
    def tail_style(self):
        return self._tailStyle
                   
    def end_point_pressed(self, point, pos):
        """
        pos - in point's local coordinates.
        """
        self.mouse_pressed_end_point.emit(point, pos)
        if self.point_item(point) is not None:
            self.set_point_item(point, None)
        else:
            scene_pos = point.mapToScene(pos)
            if self.scene():
                items = self.scene().items(scene_pos)
                
                for item in items:
                    if isinstance(item, (Arrow, widget.node.Node)):
                        if not self.is_ancestor_of(item, self) and not self.is_ancestor_of(self, item):
                            self.set_point_item(point, item)
                            break
                        
        
    def end_point_released(self, point, pos):
        self.mouse_released_end_point.emit(point, pos)
        if self.scene():
            scene_pos = point.mapToScene(pos)
            items = self.scene().items(scene_pos)
            
            if self.point_item(point) is not None:
                self.set_point_item(point, None)
            else:       
                for item in items:
                    if not self.is_ancestor_of(item, point):
                        item = self.closest_ancestor_of_type(item, (widget.node.Node, Arrow))
                        if item:
                            self.set_point_item(point, item)
                            break
                        
    def set_point_item(self, point, item):
        if point is self.source_point:
            self.set_source(item)
        elif point is self.destination_point:
            self.set_destination(item)
            
    def point_item(self, point):
        if point is self.source_point:
            return self.source
        elif point is self.destination_point:
            return self.destination
            
    def _popupBezier(self, point):
        if not self.is_bezier:
            assert self.source == self.destination
            self.arrow_style.set_bezier()
            pos = self.source.mapToScene(self.source.closest_boundary_pos_to(point))
            pos = self.mapFromScene(pos)
            center = self.mapFromScene(self.source.scenePos())
            v = pos - center
            perp = QPointF(-v.y(), v.x())
            u = v + center
            a = u + perp
            b = u - perp 
            item_shape = self.source.paint_shape()
            a = closest_point_on_path(a, self.mapFromItem(self.source, item_shape))
            b = closest_point_on_path(b, self.mapFromItem(self.source, item_shape))
            self._points[0].setPos(a)
            self._points[-1].setPos(b)
            a += 2*v + perp
            b += 2*v - perp
            self._points[1].setPos(a)
            self._points[-2].setPos(b)
           
    @property
    def source_or_point(self):
        if self._source is None:
            return self.source_point
        return self._source
       
    @property
    def destination_or_point(self):
        if self.destination is None:
            return self.destination_point
        return self.destination    

    @property
    def destination_point(self):
        return self._points[-1]
    
    @property
    def source_point(self):
        return self._points[0]
    
    @property
    def connect_padding(self):
        return self._connectPad
    
    def set_connect_padding(self, pad):
        if pad != self._connectPad:
            self._connectPad = pad
            self.update()
    
    def boundingRect(self):
        h = self.head_size / 2.0
        rect = self.childrenBoundingRect().adjusted(-h, -h, h, h) # BUGFIX: now labels are contained inside grouping nodes
        return rect

    @property
    def is_bezier(self):
        return self.arrow_style.is_bezier

    def set_line(self, line):
        self._points[0].setPos(line.p1())
        self._points[-1].setPos(line.p2())
        self.update()
        
    @property
    def num_heads(self):
        return self._headStyle  # yes, this is right, check the enum
    
    @property
    def head_size(self):
        return self._relativeHeadSize * self.pen.widthF()    
        
    def set_line_points(self, pos0, pos1):
        u = pos1 - pos0
        mag_u = mag2D(u)
        u /= (len(self._points) - 1)
        for k in range(0, len(self._points)):
            self._points[k].setPos(pos0 + k*u)
        
    def _toggleBezierControlPoints(self, toggled):
        # Do not call this directly.  Only as a callback for ArrowStyle.  TODO
        # Use instead an accesor method to toggle the bezier style through our arrow_style member, or create one if it doesn't exist. :)
        self._bezier = toggled
        self._points[1].setVisible(toggled)
        self._points[2].setVisible(toggled)
        self.bezier_toggled.emit(toggled)
        self.set_line_points(self._points[0].pos(), self._points[-1].pos())

    @property            
    def line(self):
        return QLineF(self._points[0].pos(), self._points[-1].pos())
    
    def update_control_point_positions(self):
        if not self._updatingPointPos:
            self._updatingPointPos = True
            self.prepareGeometryChange()
            source = self.source_or_point
            dest = self.destination_or_point

            if not self.is_bezier:
                if isinstance(source, Arrow):
                    a = closest_point_on_path(source.mapFromItem(dest, dest.boundingRect().center()), source.line_shape())
                else:
                    a = closest_point_on_path(source.mapFromItem(dest, dest.boundingRect().center()), source.paint_shape())
                
                if isinstance(dest, Arrow):
                    b = closest_point_on_path(dest.mapFromItem(source, a), dest.line_shape())                    
                else:
                    b = closest_point_on_path(dest.mapFromItem(source, a), dest.paint_shape())
            else:
                if isinstance(source, Arrow):
                    a = closest_point_on_path(source.mapFromItem(dest, dest.boundingRect().center()), source.line_shape())
                else:
                    a = source.closest_boundary_pos_to(self._points[1])
                    
                if isinstance(dest, Arrow):
                    b = closest_point_on_path(dest.mapFromItem(source, a), dest.line_shape())
                else:
                    b = dest.closest_boundary_pos_to(self._points[2])
                              
            if a and b:
                a = self.mapFromItem(source, a)
                b = self.mapFromItem(dest, b)
            else:
                return
                
            if self.destination is not None:
                self.destination_point.setPos(b) 
            if self.source is not None:
                self.source_point.setPos(a) 

            if not self.is_bezier:
                self.set_line_points(self._points[0].pos(), self._points[-1].pos())

            self.update_text_position()
            self._updatingPointPos = False
                   
    @property
    def label_pos_line(self):
        if not self.is_bezier:
            line = QLineF(self._points[0].pos(), self._points[-1].pos())    
        else:
            line = QLineF(self._points[1].pos(), self._points[-2].pos())
        return line

    def update_text_position(self):
        line = self.label_pos_line
        last_line = self._lastLabelPosLine
        if last_line is None:
            self._lastLabelPosLine = line
            return        
        du = line.p1() - last_line.p1()
        dv = line.p2() - last_line.p2()
        delta = (du + dv) / 2
        for c in self.childItems():
            if isinstance(c, Text):
                c.setPos(c.pos() + delta)
        self._lastLabelPosLine = line

    @property
    def control_points(self):
        return self._points
    
    def is_end_point(self, ctrl_pt):
        points = self.control_points
        if points[-1] is ctrl_pt or points[0] is ctrl_pt:
            return True
        return False

    def control_points_center(self):
        center = QPointF()
        for point in self._points:
            center += point.pos()
        center /= len(self._points)
        return center           
        
    def setEditable(self, editable):
        super().setEditable(editable)
        super().setEditable(editable)
    
    def center_child(self, child):
        rect = child.boundingRect()
        center = self.point_center()
        child.setPos(center.x() - rect.width()/2, center.y() - rect.height()/2)      

    @property
    def tail_line(self):
        if self.is_bezier:
            return QLineF(self._points[0].pos(), self._points[1].pos())
        return QLineF(self._points[0].pos(), self._points[-1].pos())
           
    def closest_boundary_pos_to(self, item):
        shape = self.shape()
        item_shape = item.shape()
        item_shape = self.mapFromItem(item, item_shape)
        if shape and item_shape:
            point = closest_point_on_path(item_shape.boundingRect().center(), shape)
            point = closest_point_on_path(point, item_shape)
            point = closest_point_on_path(point, shape)   # A 3rd order approximation is fine!
            return point
    
    def _updatePaintPath(self):
        self.arrow_style.update_all([p.pos() for p in self._points], self.pen.widthF())
        stroker = QPainterPathStroker()
        stroker.setCapStyle(Qt.RoundCap)
        stroker.setJoinStyle(Qt.RoundJoin)
        stroker.setWidth(self.arrow_style.head_width)
        self._intersectShape = stroker.createStroke(self.arrow_style.paint_path)
        
    def line_shape(self):
        return self.arrow_style.line_path
           
    def _updateSelectionPath(self):
        #pad = self._boundingRectPadding
        path = QPainterPath()
        path.addPath(self.arrow_style.line_path)
        path.addPath(self.arrow_style.head_path)
        self._selectionPath = path
    
    #def build_context_menu(self, event):
        #menu = super().build_context_menu(event)
        #menu.addSeparator()
        #bezier = menu.addAction("Bezier")
        #bezier.setCheckable(True)
        #bezier.setChecked(self.is_bezier)
        #bezier.toggled.connect(self.toggle_bezier)
        #menu.addSeparator()
        #return menu
    
    def update_centroid_position(self):
        pass
        #self._updatingPointPos = True
        #center = self.point_center()
        #delta = self.pos() - center
        ##for point in self._points:
            ##point.setPos(ce1
        ###delta = self.mapFromParent(delta)
        #for point in self._points:
            #point.setPos(point.pos() + delta)
        #self._updatingPointPos = False
    
    def point_center(self):
        c = QPointF()
        for point in self._points:
            c += point.pos()
        return c / len(self._points)
                                       
    def opposite_item(self, item):
        if self.source is item:
            return self.destination_or_point()
        return self.source_or_point()
    
    def root_and_opposite_item(self):
        items = [self.source, self.destination()]
        root = None
        for i in items:
            if i is not None:
                root = i
                break
        if root:
            remote = self.opposite_item(root)
            return root, remote
        return None, None
    
    def arrow_list_parallel_with_this(self, sort_key=None):
        root, remote = self.root_and_opposite_item()
        if root:
            lst = list(root.parallel_arrow_list(remote))
            if sort_key is not None:
                lst.sort(key=sort_key)
            return lst
        
    def set_point_pos(self, item, pos):
        if item is self.source_or_point():
            self.source_point().setPos(pos)
        else:
            self.destination_point().setPos(pos)

    def source_can_be(self, item):
        """
        For reasons of hard-to-fix bugs, we only allow same-parent for source & target.
        """        
        dest = self.destination
        if isinstance(item, (Arrow, gfx.object.Object, type(None))):      
            # ^^^ For instance you can't connect to a control point
            if dest is not None:
                if item is not None:
                    if dest.parentItem() is item.parentItem():
                        #if type(tar) == type(item):
                            #if item.math_type() == tar.math_type():
                        return True
                    return False
            return True
        return False
    
    def destination_can_be(self, item):
        """
        For reasons of hard-to-fix bugs, we only allow same-parent for source & target.
        """
        src = self.source
        if isinstance(item, (Arrow, gfx.object.Object, type(None))):
            if src is not None:
                if item is not None:
                    if src.parentItem() is item.parentItem():
                        return True
                    return False
            return True
        return False
    
    def set_at_point(self, ctrl_point:ControlPoint, item:Connectable):
        if ctrl_point is self.destination_point:
            self.set_destination(item)
        elif ctrl_point is self.source_point:
            self.set_source(item)
    
    def set_source(self, src):
        if self.source_can_be(src):
            #if src is None:
                #self.undo_setup_source()
            if src is not self.source and isinstance(src, (Arrow, gfx.object.Object, type(None))):
                #if self._source is not None:
                    #self.undo_setup_source()
                    #self._source.undo_setup_out_arrow(self)
                super().set_source(src)
                #if src is not None:
                    #src.setup_out_arrow(self)
                if src and src is self.destination:
                    self._popupBezier(self.source_point)
                self.update()
            if src:
                p = src.parentItem()
                self.setParentItem(p)
    
    def set_destination(self, dest):
        if self.destination_can_be(dest):
            #if tar is None:
                #pass
                #self.undo_take_image()
            if dest is not self.destination and isinstance(dest, (Arrow, gfx.object.Object, type(None))):
                #if self.destination is not None:
                    #self.destination.undo_setup_in_arrow(self)
                super().set_destination(dest)
                #if tar is not None:
                    #tar.setup_in_arrow(self)
                if dest and dest and dest is self.source:
                    self._popupBezier(self.destination_point)
                self.update()          
            if dest:
                p = dest.parentItem()
                self.setParentItem(p)
                   
    def end_at_point_can_be(self, item, point):
        if point is self.destination_point():
            return self.destination_can_be(item)
        elif point is self.source_point():
            return self.source_can_be(item)
    
    @property
    def line_spacing(self):
        return self.head_size / self.head_pointedness
    
    @property
    def head_pointedness(self):
        return self._pointedness
           
    def parenthesize(self, arg):
        arg = arg.strip('$')
        #TODO: remove this or fix crash:
        #if arg in alphabet:
            #return arg
        return "(" + arg + ")"
    
    def hoverEnterEvent(self, event):
        window = QApplication.activeWindow()
        if self.scene() and window.language_edit_mode in (window.ArrowMode, window.MoveMode):
            if self._editTimer:
                self._editTimer.stop()
            self.set_control_points_visible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        window = QApplication.instance().topmost_main_window
        if self.scene() and window.language_edit_mode in (window.ArrowMode, window.MoveMode):            
            if self._editTimer:
                self._editTimer.stop()
            self._editTimer = QTimer()
            self._editTimer.setSingleShot(False)
            self._editTimer.timeout.connect(self._hoverLeaveEvent)
            self._editTimer.setInterval(self.control_point_edit_time)
            self._editTimer.start()
        super().hoverLeaveEvent(event)
            
    def set_control_points_visible(self, visible:bool):
        if self.is_bezier:
            points = self._points
        else:
            points = (self._points[0], self._points[-1])
        for point in points:
            point.setVisible(visible)            

    def _hoverLeaveEvent(self):
        self.set_control_points_visible(False)
        self._editTimer.stop()
        self._editTimer = None
    
    def set_color(self, col:QColor):
        self.setPen(set_pen_color(self.pen(), col))
        
    def color(self):
        return self.pen.color()
    
    def source_or_target_point(self, point:ControlPoint) -> str:
        if point is self.source_point:
            return 'source'
        elif point is self.destination_point:
            return 'target'
        
    def paint(self, painter, option, widget):
        if self.isSelected() and self.scene():
            paint_selection_shape(painter, self._selectionPath, self.transform(),
                                  self.transformations(), self.scene().backgroundBrush().color())
        shape = self.arrow_style.paint_path
        if shape:
            painter.setRenderHints(painter.Antialiasing | painter.HighQualityAntialiasing)    
            painter.setPen(self.pen)
            painter.drawPath(shape)   
            
    def shape(self):
        return self._intersectShape
    
    def paint_shape(self):
        return self._shape
            
    @property
    def source_or_point(self):
        if self.source is None:
            return self.source_point
        return self.source
    
    @property
    def target(self):
        return self._target
    
    @property
    def target_or_point(self):
        if self.destination is None:
            return self.destination_point
        return self.destination
    
    def update(self): 
        try:            
            self.prepareGeometryChange()
            
            if self.scene():
                if id(self) not in self.scene().items_being_moved:
                    self.update_control_point_positions()
            else:
                self.update_control_point_positions()
                
            self._updateBoundingBox()    
            self._updatePaintPath()
            self._updateSelectionPath()
            QGraphicsObject.update(self)
        except Exception as excep:
            raise excep
        #if self.parentItem():
            #self.parentItem().update()
        
    #def sceneEventFilter(self, watched, event):
        #if isinstance(watched, ControlPoint):
            #if event.type() in (QEvent.GraphicsSceneHoverMove, QEvent.GraphicsSceneMouseMove):
                #self.update()
                #self.update_connectors()
        #return super().sceneEventFilter(watched, event)
    
    def build_context_menu(self, menu:QMenu=None):
        if menu is None:
            menu = QMenu()        
        styleMenu = menu.addMenu('Style')
        self.arrow_style.build_context_menu(styleMenu)
        GraphicsShape.build_context_menu(self, menu)
        Containable.build_context_menu(self, menu)
        Deletable.build_context_menu(self, menu)   
        return menu
    
    @property
    def line_count(self):
        return self._lineCount
    
    def set_line_count(self, count:int):
        if count != self._lineCount:
            self._lineCount = count
            self.update()
            
    def shape_box(self):        
        children = self.childItems()
        shapeBox = QRectF()
        for c in children:
            if not isinstance(c, ControlPoint):
                if isinstance(c, Containable) and c.contained_in_bbox:
                    if isinstance(c, GraphicsShape):
                        shapeBox = shapeBox.united(c.shape_box().translated(c.pos()))        
                    elif isinstance(c, Text):
                        shapeBox = shapeBox.united(c.boundingRect().translated(c.pos()))
                else:
                    shapeBox = shapeBox.united(c.boundingRect().translated(c.pos()))
        shapeBox = shapeBox.united(self.shape().boundingRect())    # BUGFIX  
        return shapeBox            
    
    @staticmethod
    def set_default_pen_color(color):
        Arrow.default_color = color
        
