from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from collections import OrderedDict
from graphics.containable import Containable
from graphics.snappable import Snappable

class CollisionResponsive:
    Epsilon = 0.01
    _memo = set()
    
    @staticmethod
    def moved_items():
        return CollisionResponsive._movedItems
    
    def bbox_collision_response(self):
        self._memo.clear()
        self._bboxCollisionResponse()
        
    def _bboxCollisionResponse(self):
        from graphics.text import Text
        if not QApplication.instance().topmost_main_window().collision_response_enabled:
            return
        if not self.scene():
            return        
        if isinstance(self, Snappable) and self.snap_to_grid and self.scene().snap_grid_enabled():
            return
        if id(self) in  self._memo:
            return
        self._memo.add(id(self))
        colliding = self.collidingItems(Qt.IntersectsItemBoundingRect)
        if not QApplication.instance().topmost_main_window().text_collision_response_enabled:
            colliding = filter(lambda x: not isinstance(x, Text), colliding)
        colliding = filter(lambda x: not self.isAncestorOf(x) and not x.isAncestorOf(self), colliding)
        to_filter = colliding
        colliding = []
        for item in to_filter:
            for item1 in colliding:
                if item1.isAncestorOf(item):
                    if isinstance(item, Containable) and not item.contained_in_bbox:
                        colliding.append(item)
                    break
            else:
                colliding.append(item)        
        for item in colliding:
            parent = item.parentItem()
            if parent and isinstance(item, Containable) and not item.contained_in_bbox and \
               not parent.isAncestorOf(self):
                move_item = item.parentItem()
            else:
                move_item = item
            if not isinstance(move_item, CollisionResponsive) or \
               (isinstance(move_item, Snappable) and move_item.snap_to_grid and self.scene().snap_grid_enabled()):
                continue
            rect = self.mapToItem(item, self.boundingRect()).boundingRect().intersected(item.boundingRect())
            center_delta = item.boundingRect().center()- self.mapToItem(item, self.boundingRect().center())
            if rect.width() <= rect.height():
                dx = rect.width() + self.Epsilon
                if center_delta.x() >= 0:
                    move_item.moveBy(dx, 0)
                else:
                    move_item.moveBy(-dx, 0)
            else:
                dy = rect.height() + self.Epsilon
                if center_delta.y() >= 0:
                    move_item.moveBy(0, dy)
                else:
                    move_item.moveBy(0, -dy)
            move_item._bboxCollisionResponse()
                
    def _itemChange(self, change, value):
        if change == self.ItemPositionHasChanged:
            self.bbox_collision_response()
        return value                
            

