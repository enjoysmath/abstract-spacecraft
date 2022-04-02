from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtCore import Qt, QPointF

class Snappable:
    def __init__(self):
        self._snapToGrid = True   
        self._snapDelta = QPointF()
    
    @property
    def snap_to_grid(self):
        return self._snapToGrid
    
    def set_snap_to_grid(self, snap:bool=True):
        if self._snapToGrid != snap:
            self._snapToGrid = snap
            self.update()
            
    def snap_to_grid_pos(self, value):
        scene = self.scene()
        if scene:        
            if self.snap_to_grid and scene.snap_grid_enabled():
                #if QApplication.mouseButtons() == Qt.LeftButton:
                gridSizex = scene.grid_sizex()
                gridSizey = scene.grid_sizey()
                o = scene.grid_origin()
                ox = o.x() % gridSizex
                oy = o.y() % gridSizey

                x = round(value.x() / gridSizex) * gridSizex
                y = round(value.y() / gridSizey) * gridSizey
                value = QPointF(x + ox, y + oy) 
                        
        return value  # BUGFIX: this was causing major issues when it was inside the above hasattr check
    
    def _mouseReleaseEvent(self, event):
        self.setPos(self.pos(), snap=True)
    
    def _setPos(self, pos:QPointF):
        #if self.snap_to_grid:
            #pos = self.snap_to_grid_change_pos(pos)
        return pos
    
    def build_context_menu(self, menu:QMenu):
        action = menu.addAction('Snap to grid')
        action.setCheckable(True)
        action.setChecked(True)
        action.toggled.connect(self.set_snap_to_grid)
        
    def compute_top_left_grid_point(self, point):
        scene = self.scene()
        gridSizeX = scene.grid_sizex()
        gridSizeY = scene.grid_sizey()
        x = int(point.x() / gridSizeX) * gridSizeX
        y = int(point.y() / gridSizeY) * gridSizeY
        return QPointF(x, y)