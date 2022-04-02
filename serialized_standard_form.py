from object import Object
from arrow import Arrow
from text import Text
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import htmlmin
from bidict import bidict
from functools import cmp_to_key

## Arrow / Object / Text are PyQt5 QGraphicsObjects subclasses.  An Arrow is an Object and so
## is connectable by other arrows.  This serialization has to support that.

class SerializedObject:
    def __init__(self, degree:int, labels:list):
        self._labels = labels
        self._degree = degree
        
    @property
    def total_degree(self):
        return self._degree
        
    def variablize(self, variables:dict):
        labels = self._labels
        labelsModVars = []
        # Variablize once first in order to take out the variables and get
        # a natural lexicographic ordering on the literal strings (canonization):
        for label in labels:
            labelModVars = SerializedLabel(label)
            labelModVars.variablize({})
            labelsModVars.append((str(labelModVars), label))
        labelsModVars.sort(key=lambda t: t[0])  # Sort lexicographically with no variables (the literals)
        # Variablize a second time for the final product:
        for k in range(len(labels)):
            label = labelsModVars[k][1]
            label = SerializedLabel(label)
            label.variablize(variables)
            labels[k] = label
            
    def __str__(self):
        return repr(self._labels)

class SerializedArrow(SerializedObject):
    def __init__(self, degree:int, labels:list, source:int, dest:int):
        super().__init__(degree, labels)
        self._source = source
        self._dest = dest
    
    def __str__(self):
        return f'{self._source}-{self._labels}->{self._dest}'

class SerializedLabel:
    _languageLiteralTags = set(('b', 'i', 'strong', 'p'))
    
    def __init__(self, html:str):
        self._variables = bidict()
        self._text = html
        self._soup = BeautifulSoup(html, "html.parser")
        self._standardForm = None
                 
    @staticmethod
    def standardize(soup:BeautifulSoup) -> str:
        html = soup.prettify()
        html = "".join(line.strip() for line in html.split('\n'))
        html = htmlmin.minify(html, remove_all_empty_space=True)        
        return html
    
    def variablize(self, variables:bidict):
        elem = self._soup
        existing_vars = bidict(variables)
        self._standardForm = self.standardize(self._variablize(variables, elem))
        self._variables = bidict({ var: index for var,index in variables.items() if var not in existing_vars })
                
    @staticmethod
    def _variablize(variables:dict, elem):     
        if isinstance(elem, NavigableString):                                   
            string = ''            
            for c in elem:
                if c != ' ':
                    if c not in variables:
                        variables[c] = len(variables)
                    string += f'{{_{variables[c]}}}'
                else:
                    string += c                
            return NavigableString(string)                                    
        if elem.name not in SerializedLabel._languageLiteralTags:
            for k in range(len(elem.contents)):
                elem.contents[k] = SerializedLabel._variablize(variables, elem.contents[k])
                
        return elem                
                
    def __str__(self):
        return self._standardForm
    
    def __repr__(self):
        return str(self)
    
    def modulo_vars_string(self):
        subs = { f'_{i}': '' for var,i in self._variables.items() }
        return self._standardForm.format(**subs)
            
class SerializedStandardForm:
    """
    Of a diagram consisting of objects, arrows, and their labels. 
    """
    def __init__(self, objects:list, arrows:list):
        objects = objects + arrows
        indexMap = { id(o) : k for k,o in enumerate(objects) }
        add_objects = []
        
        for k,ob in enumerate(objects):
            parent = ob.parentItem()
            if id(parent) in indexMap:
                parentArrow = SerializedArrow(0, ['<b>@</b>'], indexMap[id(ob)], indexMap[id(parent)])
                add_objects.append(parentArrow)
                            
            labels = [txt.toHtml() for txt in ob.childItems() if isinstance(txt, Text)]
            
            if isinstance(ob, Arrow):
                sourceIndex = id(ob.source)
                if sourceIndex in indexMap:
                    sourceIndex = indexMap[sourceIndex]
                else:
                    sourceIndex = -1
                destIndex = id(ob.destination)
                if destIndex in indexMap:
                    destIndex = indexMap[destIndex]
                else:
                    destIndex = -1
                
                objects[k] = SerializedArrow(ob.total_degree, labels, sourceIndex, destIndex)
            else:
                objects[k] = SerializedObject(ob.total_degree, labels)
        objects += add_objects        
        objects.sort(key=cmp_to_key(self._sortCompare))                
        
        variables = bidict()
        
        for o in objects:
            o.variablize(variables)
            
        self._objects = objects
        
    @staticmethod
    def _sortCompare(x, y):
        if x.total_degree > y.total_degree:
            return -1
        if x.total_degree < y.total_degree:
            return 1
        x = str(x)
        y = str(y)
        if len(x) > len(y):
            return -1
        if len(x) < len(y):
            return 1
        if x < y:
            return -1
        if y > x:
            return 1
        return 0
        
    def __str__(self):
        return str(list(map(str, self._objects))).replace(' ', '')
        
    def __repr__(self):
        return str(self)
    

if __name__ == '__main__':
    from PyQt5.QtWidgets import *
    import sys
    app = QApplication([])
    
    window = QMainWindow()
    window.show()
    
    #text = Text(html="G <b>:Grp</b>")    # Result should be: G is a variable and :Grp is literal text.
    #label = SerializedLabel(text)
    #variables = bidict()
    #label.variablize(variables)
    #print(label)
    #print(variables)
    #print(label.modulo_vars_string())
    
    #ob = Object("G <b>:Grp</b>")
    #text = Text("A <b>:Ab</b>")
    #text.setParentItem(ob)
    #serOb = SerializedObject(ob)
    #variables = bidict()
    #serOb.variablize(variables)
    #print(serOb._labels)
    
    ob1 = Object("A")
    ob2 = Object("B")
    ob3 = Object("<b>Ab</b>")
    
    ob1.setParentItem(ob3)
    ob2.setParentItem(ob3)
    
    arr1 = Arrow("f")
    arr1.setParentItem(ob3)
    arr1.set_source(ob1)
    arr1.set_destination(ob2)
    
    objects = [ob1, ob2, ob3]
    arrows = [arr1]
    
    standardForm = SerializedStandardForm(objects, arrows)
    string = repr(standardForm)
    print(string)
        
    sys.exit(app.exec_())