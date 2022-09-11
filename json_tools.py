mainfrom PyQt5.QtCore import *
from PyQt5.QtGui import *

def rect_to_json(rect) -> list:
    return [rect.x(), rect.y(), rect.width(), rect.height()]

def color_to_json(col:QColor) -> list:
    return [col.red(), col.green(), col.blue(), col.alpha()]

def topological_compare(item1, item2):
    if item1 is item2:
        return 0
    elif item1.isAncestorOf(item2):
        return 1
    elif item2.isAcestorOf(item1):
        return -1
    else:
        return 0
