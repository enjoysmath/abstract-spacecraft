from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from checkable_tree_item import CheckableTreeItem
from tree_widget_item import TreeWidgetItem

class TreeWidget(QTreeWidget):
    def __init__(self, new=True):
        super().__init__()
        
    def __setstate__(self, data):
        self.__init__(new=False)
        self.unpickle(data)
        
    def unpickle(self, data):
        self.setheaderLabels(data["header labels"])
        for top_item, widget in data["top items"]:
            self.addTopLevelItem(top_item)
            self.setItemWidget(top_item, 0, widget)
        
    def pickle(self):
        data = {
            "top items": [(self.topLevelItem(k), self.itemWidget(self.topLevelItem(k))) for k in range(0, self.topLevelItemCount())],
            "header labels": [],
        }
        header = self.headerItem()
        for i in range(0, header.columnCount()):
            data["header labels"].append(header.text(i))
        return data
    
    def __getstate__(self):
        return self.pickle()
        
    def getAllItems(self, item=None):
        items = []
        if item is None:
            for k in range(0, self.topLevelItemCount()):
                top_item = self.topLevelItem(k)
                items.extend(self.getAllItems(item=top_item))
        else:
            items.append(item)
            for k in range(0, item.childCount()):
                child_item = item.child(k)
                items.extend(self.getAllItems(item=child_item))
        return items
    
    def getItemText(self, item):
        if self.itemWidget(item, 0) is None:
            return item.text(0)
        return self.itemWidget(item, 0).lineEdit.text()
    
    def getItemsWithText(self, text, item=None):
        items = []
        if item is None:
            for k in range(0, self.topLevelItemCount()):
                top_item = self.toplevelItem(k)
                items.extend(self.getItemsWithText(item=top_item))
        else:
            if self.getItemText(item) == text:
                items.append(item)
            for k in range(0, item.childCount()):
                child_item = item.child(k)
                items.extend(self.getItemsWithText(item=child_item))
        return items
    
    def getItemsWithParentText(self, text, item=None):
        items = []
        if item is None:
            for k in range(0, self.topLevelItemCount()):
                top_item = self.topLevelItem(k)
                items.extend(self.getItemsWithParentText(text, item=top_item))
        else:
            if item.parent() and self.getItemText(item.parent()) == text:
                items.append(item)
            for k in range(0, item.childCount()):
                child_item = item.child(k)
                items.extend(self.getItemsWithParentText(text, item=child_item))
        return items        
                
    def setAllItemsCheckable(self):
        items = self.getAllItems()
        for item in items:
            text = item.text(0)
            item.setText(0, '')
            checkable_item = CheckableTreeItem()
            checkable_item.lineEdit.setText(text)
            self.setItemWidget(item, 0, checkable_item)
    
    def setItemsWithParentTextEditable(self, text):
        items = self.getItemsWithParentText(text)
        for item in items:
            if self.itemWidget(item, 0) is not None:
                self.itemWidget(item, 0).lineEdit.setReadOnly(False)
            else:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
        
    def buildTree(self, str_tree, item=None):
        if item is None:
            for key, tree in str_tree.items():
                top_item = TreeWidgetItem([key])
                self.addTopLevelItem(top_item)
                self.buildTree(tree, top_item)
        else:
            if isinstance(str_tree, dict):
                for key, tree in str_tree.items():
                    child_item = TreeWidgetItem([key])
                    item.addChild(child_item)
                    self.buildTree(tree, child_item)
            else:
                child_item = TreeWidgetItem([str_tree])
                item.addChild(child_item)