from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF, QTimer, QEvent, QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsSceneMouseEvent, QMenu, QAction
from PyQt5.QtGui import (QPainter, QPainterPath, QPolygonF, QPainterPathStroker, QColor,
                         QTransform, QVector2D, QPen)
from core.geom_tools import (mag2D, dot2D, rect_to_poly, paint_selection_shape, compute_quadratic_bezier, \
                        cubic_bezier_derivative, compute_cubic_bezier, approx_cubic_bezier_length, \
                        closest_point_on_path)
from math import acos, asin, atan2, pi, sin, cos, sqrt
from core.qt_tools import Pen, set_pen_style, SimpleBrush, set_pen_color, set_pen_width
from dialog.integer_spin_dialog import IntegerSpinDialog
from dialog.double_spin_dialog import DoubleSpinDialog
from dialog.combo_box_dialog import ComboBoxDialog
from bidict import bidict

NoTail, VeeTail, HookTail, OppHeadTail, FlatTail = range(5)
Linear, TriangleWavy, SineWavy = range(3)

tail_styles = [NoTail, VeeTail, HookTail, OppHeadTail, FlatTail]
line_styles = [Linear, TriangleWavy, SineWavy]

text_to_tail_style = bidict({
    'No tail' : NoTail, 
    'Vee tail' : VeeTail,
    'Hook tail' : HookTail,
    'Opposite-head tail' : OppHeadTail,
    'Flat tail' : FlatTail,
})

text_to_line_style = bidict({
    'Linear' : Linear,
    'Triangle wavy' : TriangleWavy,
    'Sine wavy' : SineWavy,
})

class ArrowStyle(QObject):
    update_requested = pyqtSignal()     
    #bezier_toggled = pyqtSignal(bool)

    MaxNumLines = 3
    MaxNumHeads = 6
    MaxCurvature = 20.0
    MinCurvature = -20.0
    ColinearEpsilon = 0.5

    def __init__(self):
        super().__init__()
        self._numHeads = 1
        self._numTails = 1
        self._curvature = 3.0
        self._headLength = 20.0
        self._headWidth = 10.0       
        self._numLines = 1
        self._lineStyle = Linear        
        self._tailStyle = NoTail
        self._relPenHeadSpace = 3.5
        self._polylineSubdivPer100Px = 12
        self._polylineSubdiv = None
        self._polylineWidthParam = 0.7

        self._headPath = QPainterPath()
        self._linePath = QPainterPath()
        self._tailPath = QPainterPath()
        self._allPath = QPainterPath()

        self._isBezier = False
        self._headPoints = None     # Used for updating the line path ones we know the head control points
        self._tailPoints = None
        self._paintPath = QPainterPath()        
        self._selectionPath = QPainterPath()

    @property
    def paint_path(self):
        return self._paintPath

    @property
    def head_path(self):
        return self._headPath

    @property
    def line_path(self):
        return self._linePath

    @property
    def tail_path(self):
        return self._tailPath

    def update_head(self, points, pen_width):
        self._headPath.clear()

        if self._numHeads == 0:
            self._headPoints = self._headControlPoints(points)
            return
        
        if self._isBezier:
            line = QLineF(points[-2], points[-1])
        else:
            line = QLineF(points[0], points[-1])

        headPath = QPainterPath()
        P = self._headControlPoints(points)

        headPath.moveTo(P[0])
        headPath.quadTo(P[1], P[2])
        headPath.quadTo(P[3], P[4])

        self._headPath.addPath(headPath)

        if self._numHeads > 1:        
            t = QVector2D(line.p1() - line.p2())
            t.normalize()
            t = t.toPointF()
            headSpace = self._relPenHeadSpace * pen_width * t

            for k in range(1, self._numHeads):
                headPath.translate(headSpace)
                self._headPath.addPath(headPath)
                
            self._headPoints = tuple(point + k*headSpace for point in P)
        else:
            self._headPoints = P

    def _headControlPoints(self, points):
        arrowTip = points[-1]  

        if self._isBezier:
            point = points[-2]
        else:
            point = points[0]    

        h = QLineF(arrowTip, point)    # v will be from head to tail
        h = h.unitVector()
        b = h.normalVector()
        h = h.p2() - h.p1()
        b = b.p2() - b.p1()
        h *= self._headLength        
        b = b * self._headWidth / 2

        if self._numHeads == 0:
            v = b
            curvature = 0
        else:
            v = b + h
            curvature = self._curvature        
        
        u = v
        midDiag = v / 2
        v = QLineF(QPointF(), v)
        v = v.normalVector()
        v = v.unitVector()
        v = v.p2() - v.p1()
        midDiag += arrowTip
        points = (u + arrowTip, midDiag + -curvature * v, arrowTip)

        b = -b

        if self._numHeads == 0:
            v = b
        else:
            v = b + h
            
        u = v
        midDiag = v / 2
        v = QLineF(QPointF(), v)
        v = v.normalVector()
        v = v.unitVector()
        v = v.p2() - v.p1()
        midDiag += arrowTip
        points += (midDiag + curvature * v, u + arrowTip)

        return points             

    def _tailControlPoints(self, points):
        arrowTip = points[0]  

        if self._isBezier:
            cPoint = points[1]
        else:
            cPoint = points[-1]   
            
        if self._tailStyle == VeeTail:
            temp = arrowTip
            arrowTip = cPoint
            cPoint = temp

        h = QLineF(arrowTip, cPoint)    
        h = h.unitVector()
        b = h.normalVector()
        h = h.p2() - h.p1()
        b = b.p2() - b.p1()
        h *= self._headLength        
        b = b * self._headWidth / 2
        
        if self._tailStyle == VeeTail:
            arrowTip = cPoint - h
        
        if self._tailStyle in (NoTail, FlatTail):
            v = b
            curvature = 0
        else:
            v = b + h
            curvature = self._curvature
            
        u = v
        midDiag = v / 2
        v = QLineF(QPointF(), v)
        v = v.normalVector()
        v = v.unitVector()
        v = v.p2() - v.p1()
        midDiag += arrowTip
        points = (u + arrowTip, midDiag - curvature*v, arrowTip)

        b = -b
        
        if self._tailStyle in (NoTail, FlatTail):
            v = b
        else:
            v = b + h
            
        u = v
        midDiag = v / 2
        v = QLineF(QPointF(), v)
        v = v.normalVector()
        v = v.unitVector()
        v = v.p2() - v.p1()
        midDiag += arrowTip
        points += (midDiag + curvature*v, u + arrowTip)

        return points

    def update_line(self, points, pen_width):
        points1 = list(points)
        self._linePath.clear()

        if self._numLines == 0:
            return    

        if self._isBezier:
            headLine = QLineF(points[2], points[3])
            tailLine = QLineF(points[1], points[0])
        else:
            headLine = QLineF(points[0], points[3])
            tailLine = headLine
            
        t = self._polylineWidthParam            
        head = compute_quadratic_bezier(t, self._headPoints[2:5])
        tail = compute_quadratic_bezier(t, self._tailPoints[2:5])
        
        u = headLine.unitVector()
        u = u.p2() - u.p1()        
        d = QVector2D(head).distanceToLine(QVector2D(headLine.p1()), QVector2D(u))
        
        lineHeadStart = points[3] + u * self._headLength
        points1[3] = QVector2D.dotProduct(QVector2D(head - lineHeadStart), QVector2D(u)) \
            * u + lineHeadStart
        
        v = tailLine.unitVector()
        v = v.p1() - v.p2()
        
        if self._numTails != 0 and self._tailStyle != NoTail:
            lineTailStart = points[0] - v*self._headLength
        else:
            lineTailStart = points[0]
            
        points1[0] = QVector2D.dotProduct(QVector2D(tail - lineTailStart), QVector2D(v)) \
            * v + lineTailStart
            
        if self._numLines in (1,3):
            polyline0 = QPolygonF()
            if self._tailStyle != VeeTail:
                polyline0.append(points[0])
            
        polyline = QPolygonF()
        polyline1 = QPolygonF()
        
        if self._isBezier:
            N = self._polylineSubdivPer100Px * approx_cubic_bezier_length(points) / 100.0
            N = int(N)
            if N < 1:
                N = 1            
        else:
            N = 1
            
        if self._tailStyle == VeeTail:
            passedTailPoint = False
            
        tailRect = self._tailPath.boundingRect()
      
        if self._numLines in (1,3):
            polyline0.append(self._tailPoints[2])          
            
        for k in range(N + 1):
            t = k / N
            Bt = compute_cubic_bezier(t, points1)
            dB_dt = cubic_bezier_derivative(t, points1)
            line = QLineF(Bt, Bt + dB_dt)
            line = line.normalVector()
            line = line.unitVector()
            perpTan = line.p2() - line.p1()
            
            if self._numLines in (1,3):
                if self._tailStyle == VeeTail:
                    if passedTailPoint:
                        polyline0.append(Bt)
                    elif not tailRect.contains(Bt):
                        polyline0.append(Bt)                        
                        passedTailPoint = True                           
                else:
                    polyline0.append(Bt)
                
            if self._numLines in (2,3):
                polyline.append(Bt + perpTan * d)
                polyline1.append(Bt - perpTan * d)
                
        if self._numLines in (1,3):
            polyline0.append(points[3])
            self._linePath.addPolygon(polyline0)
        if self._numLines in (2,3):
            self._linePath.addPolygon(polyline)
            self._linePath.addPolygon(polyline1)

    def update_tail(self, points, pen_width):
        self._tailPath.clear()
        
        if self._numTails == 0 or self._tailStyle == NoTail:
            self._tailPoints = self._tailControlPoints(points)
            return

        if self._isBezier:
            line = QLineF(points[1], points[0])
        else:
            line = QLineF(points[-1], points[0])        

        tailPath = QPainterPath()
        P = self._tailControlPoints(points)

        tailPath.moveTo(P[0])
        tailPath.quadTo(P[1], P[2])
        tailPath.quadTo(P[3], P[4])

        self._tailPath.addPath(tailPath)
        
        if self._numTails > 1:        
            t = QVector2D(line.p1() - line.p2())
            t.normalize()
            t = t.toPointF()
            headSpace = self._relPenHeadSpace * pen_width * t

            for k in range(1, self._numTails):
                tailPath.translate(headSpace)
                self._tailPath.addPath(tailPath)
            self._tailPoints = tuple(point + k*headSpace for point in P)
        else:
            self._tailPoints = P                
                
    def update_all(self, points, pen_width):
        self.update_head(points, pen_width)
        self.update_tail(points, pen_width)  
        self.update_line(points, pen_width)      
        self._paintPath.clear()
        linePath = QPainterPath(self._linePath)
        self._paintPath.addPath(self._headPath)
        self._paintPath.addPath(linePath)
        self._paintPath.addPath(self._tailPath)
        self.update_selection_path(points, pen_width)

    def update_selection_path(self, points, pen_width):
        self._selectionPath.clear()

        if self._isBezier:
            tline = QLineF(points[0], points[1])
            hline = QLineF(points[-2], points[-1])
        else:
            tline = hline = QLineF(points[0], points[-1])

        v = tline.unitVector()
        u = v.normalVector()
        u = u.p2() - u.p1()
        v = v.p2() - v.p1()
        w = self._headWidth / 2 + pen_width/2
        arcStart = points[0] - w*u
        arcEnd = points[0] + w*u
        self._selectionPath.moveTo(arcStart)
        #self._selectionPath.arcTo(QRectF(0,0,w,w), 180, 0)

    @property
    def is_bezier(self):
        return self._isBezier

    def set_bezier(self, bezier:bool=True):
        if self._isBezier != bezier:
            self._isBezier = bezier
            self.update_requested.emit()    

    @property
    def line_style(self):
        return self._lineStyle

    def set_line_style(self, style:int):
        if style != self._lineStyle:
            self._lineStyle = style
            self.update_requested.emit()

    def show_line_style_dialog(self):
        dialog = ComboBoxDialog()
        dialog.setWindowTitle('Set line style')
        combo = dialog.comboBox
        combo.clear()
        for style in line_styles:
            combo.addItem(text_to_line_style.inv[style])
        combo.setCurrentText(text_to_line_style.inv[self.line_style])
        combo.currentTextChanged.connect(lambda s: self.set_line_style(text_to_line_style[s]))
        dialog.exec_()

    def set_tail_style(self, style:int):
        if style != self._tailStyle:
            self._tailStyle = style
            self.update_requested.emit()

    @property
    def tail_style(self):
        return self._tailStyle

    def show_tail_style_dialog(self):
        dialog = ComboBoxDialog()
        dialog.setWindowTitle('Set tail style')
        combo = dialog.comboBox        
        combo.clear()
        for style in tail_styles:
            combo.addItem(text_to_tail_style.inv[style])
        combo.setCurrentText(text_to_tail_style.inv[self.tail_style])
        combo.currentTextChanged.connect(lambda s: self.set_tail_style(text_to_tail_style[s]))  
        dialog.exec_()

    @property
    def number_of_heads(self):
        return self._numHeads
    
    @property
    def number_of_tails(self):
        return self._numTails

    def set_number_of_heads(self, heads:int):
        if self._numHeads != heads:
            self._numHeads = heads
            self.update_requested.emit()
            
    def set_number_of_tails(self, tails:int):
        if self._numTails != tails:
            self._numTails = tails
            self.update_requested.emit()

    def show_num_heads_dialog(self):
        dialog = IntegerSpinDialog()
        dialog.setWindowTitle('Set number of heads')
        spinBox = dialog.spinBox
        spinBox.setMinimum(0)
        spinBox.setMaximum(6)
        spinBox.setValue(self.number_of_heads)
        spinBox.valueChanged.connect(self.set_number_of_heads)
        dialog.exec_()
        
    def show_num_tails_dialog(self):
        dialog = IntegerSpinDialog()
        dialog.setWindowTitle('Set number of tails')
        spinBox = dialog.spinBox
        spinBox.setMinimum(0)
        spinBox.setMaximum(6)
        spinBox.setValue(self.number_of_tails)
        spinBox.valueChanged.connect(self.set_number_of_tails)
        dialog.exec_()

    @property
    def number_of_lines(self):
        return self._numLines

    def set_number_of_lines(self, lines:int):
        if self._numLines != lines:
            self._numLines = lines
            self.update_requested.emit()

    def show_num_lines_dialog(self):
        dialog = IntegerSpinDialog()
        dialog.setWindowTitle('Set number of lines')
        spinBox = dialog.spinBox
        spinBox.setMinimum(0)
        spinBox.setMaximum(self.MaxNumLines)
        spinBox.setValue(self.number_of_lines)
        spinBox.valueChanged.connect(self.set_number_of_lines)
        dialog.exec_()        

    def show_head_curvature_dialog(self):
        dialog = DoubleSpinDialog()
        dialog.setWindowTitle('Set head curvature')
        spinBox = dialog.doubleSpinBox
        spinBox.setMinimum(self.MinCurvature)
        spinBox.setMaximum(self.MaxCurvature)
        spinBox.setSingleStep(0.1)
        spinBox.setDecimals(1)
        spinBox.setAccelerated(True)
        spinBox.setValue(self._curvature)
        spinBox.valueChanged.connect(self.set_head_curvature)
        dialog.exec_()

    def set_head_curvature(self, curve):
        if curve != self._curvature:
            self._curvature = curve
            self.update_requested.emit()

    def show_head_length_dialog(self):
        dialog = DoubleSpinDialog()
        dialog.setWindowTitle('Set head length')
        spinBox = dialog.doubleSpinBox
        spinBox.setMinimum(1.0)
        spinBox.setMaximum(1000.0)
        spinBox.setSingleStep(0.1)
        spinBox.setDecimals(1)
        spinBox.setAccelerated(True)
        spinBox.setValue(self.head_length)
        spinBox.valueChanged.connect(self.set_head_length)
        dialog.exec_()

    def set_head_length(self, length):
        if length != self._headLength:
            self._headLength = length
            self.update_requested.emit()

    @property
    def head_length(self):
        return self._headLength

    def show_head_width_dialog(self):
        dialog = DoubleSpinDialog()
        dialog.setWindowTitle('Set head length')
        spinBox = dialog.doubleSpinBox
        spinBox.setMinimum(1.0)
        spinBox.setMaximum(1000.0)
        spinBox.setSingleStep(0.1)
        spinBox.setDecimals(1)
        spinBox.setAccelerated(True)
        spinBox.setValue(self.head_width)
        spinBox.valueChanged.connect(self.set_head_width)
        dialog.exec_()

    def set_head_width(self, width):
        if width != self._headWidth:
            self._headWidth = width
            self.update_requested.emit()

    @property
    def head_width(self):
        return self._headWidth

    @property
    def head_curvature(self):
        return self._curvature

    def show_head_space_dialog(self):
        dialog = DoubleSpinDialog()
        dialog.setWindowTitle('Head space relative pen width')
        spinBox = dialog.doubleSpinBox
        spinBox.setMinimum(0.0)
        spinBox.setMaximum(1000.0)
        spinBox.setSingleStep(0.1)
        spinBox.setDecimals(1)
        spinBox.setAccelerated(True)
        spinBox.setValue(self.head_space_rel_pen)
        spinBox.valueChanged.connect(self.set_head_space_rel_pen)
        dialog.exec_()

    @property
    def head_space_rel_pen(self):
        return self._relPenHeadSpace

    def set_head_space_rel_pen(self, space):
        if space != self._relPenHeadSpace:
            self._relPenHeadSpace = space
            self.update_requested.emit()

    def show_polyline_subdiv_dialog(self):
        dialog = IntegerSpinDialog()
        dialog.setWindowTitle('Set polyline subdivision amount')
        spinBox = dialog.spinBox
        spinBox.setMinimum(1)
        spinBox.setMaximum(1000)
        spinBox.setSingleStep(1)
        spinBox.setAccelerated(True)
        spinBox.setValue(self.polyline_subdiv_per_100px)
        spinBox.valueChanged.connect(self.set_polyline_subdiv_per_100px)
        dialog.exec_()

    def show_polyline_width_param_dialog(self):
        dialog = DoubleSpinDialog()
        dialog.setWindowTitle('Set multi-line width param')
        spinBox = dialog.doubleSpinBox
        spinBox.setMinimum(0.0)
        spinBox.setMaximum(1.0)
        spinBox.setSingleStep(0.01)
        spinBox.setAccelerated(True)
        spinBox.setValue(self.polyline_width_param)
        spinBox.valueChanged.connect(self.set_polyline_width_param)
        dialog.exec_()

    @property
    def polyline_width_param(self):
        return self._polylineWidthParam

    def set_polyline_width_param(self, param:float):
        if param != self._polylineWidthParam:
            self._polylineWidthParam = param
            self.update_requested.emit()

    @property
    def polyline_subdiv_per_100px(self):
        return self._polylineSubdivPer100Px

    def set_polyline_subdiv_per_100px(self, N:int):
        if N != self._polylineSubdivPer100Px:
            self._polylineSubdivPer100Px = N
            self.update_requested.emit()

    def build_context_menu(self, menu:QMenu=None):
        if menu is None:
            menu = QMenu()

        action = menu.addAction("Bezier curve")
        action.setCheckable(True)
        action.setChecked(self.is_bezier)
        action.triggered.connect(lambda: self.set_bezier(not self.is_bezier))
        menu.addAction("Number of tails...").triggered.connect(self.show_num_tails_dialog)
        menu.addAction("Tail style...").triggered.connect(self.show_tail_style_dialog)
        menu.addAction("Number of lines...").triggered.connect(self.show_num_lines_dialog)
        #menu.addAction("Line style...").triggered.connect(self.show_line_style_dialog)
        menu.addAction("Multi-line width parameter").triggered.connect(self.show_polyline_width_param_dialog)
        menu.addAction("Polyline subdiv. per 100px").triggered.connect(self.show_polyline_subdiv_dialog)
        menu.addAction("Number of heads...").triggered.connect(self.show_num_heads_dialog)
        menu.addAction("Head curvature...").triggered.connect(self.show_head_curvature_dialog)
        menu.addAction("Head length...").triggered.connect(self.show_head_length_dialog)
        menu.addAction("Head width...").triggered.connect(self.show_head_width_dialog)
        menu.addAction("Head space relative pen...").triggered.connect(self.show_head_space_dialog)
        return menu

    @property
    def selection_path(self):
        return self._selectionPath