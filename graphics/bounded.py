from PyQt5.QtGui import QVector2D
from PyQt5.QtCore import QPointF
from core.geom_tools import closest_point_on_path
#import arrow

class Bounded:
    def closest_boundary_pos_to(self, item):
        return self._closest_boundary_pos_to(item)
    
    def _closest_boundary_pos_to(self, item, shape=None, item_shape=None, rad0=0, rad1=0):
        if shape is None:
            from graphics.arrow import Arrow
            if isinstance(self, Arrow):
                shape = self._linePath
            else:
                shape = self.paint_shape()
        if item_shape is None:
            item_shape = item.paint_shape()
            
        if shape and item_shape:
            r0 = shape.boundingRect()
            r1 = self.mapFromItem(item, item_shape.boundingRect()).boundingRect()
            
            if rad0 > 0:
                s0 = r0.adjusted(rad0, rad0, -rad0, -rad0)
            else:
                s0 = r0
            if rad1 > 0:
                s1 = r1.adjusted(rad1, rad1, -rad1, -rad1)
            else:
                s1 = r1
            
            horiz = (max(s0.left(), s1.left()), min(s0.right(), s1.right()))
            vert = (max(s0.top(), s1.top()), min(s0.bottom(), s1.bottom()))

            dx = horiz[1] - horiz[0]
            dy = vert[1] - vert[0]

            c0 = r0.center()
            c1 = r1.center()

            if dx > 0 or dy > 0:
                if dx > dy:     # Shared horizontal interval is more prominent
                    if r1.left() > r0.left():
                        x = s1.left() + dx/2
                    else:
                        x = s0.left() + dx/2
                        
                    if c0.y() < c1.y():
                        y = r0.bottom()
                    else:
                        y = r0.top()
                        
                else:       # Shared vertical interval is more prominent
                    if r1.top() > r0.top():
                        y = s1.top() + dy/2
                    else:
                        y = s0.top() + dy/2
                        
                    if c0.x() < c1.x():
                        x = r0.right()
                    else:
                        x = r0.left()
                        
                return QPointF(x, y)

            return closest_point_on_path(c1, shape)                  
        
  