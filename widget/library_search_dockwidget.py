from ui.ui_library_search_dockwidget import Ui_LibrarySearchDockWidget
from PyQt5.QtWidgets import (QDockWidget, QGridLayout, QLabel, QGraphicsView, QApplication)
from PyQt5.QtCore import QRectF
from gfx.language_canvas import LanguageCanvas
from widget.file_system_tree_view import FileSystemTreeView
from core.library_compiler_thread import LibraryCompilerThread
import _pickle as pickle
from gfx.arrow import Arrow
from core.qt_tools import filter_out_descendents
from core.library_search_thread import LibrarySearchThread
from gfx.language_gfx_view import LanguageGfxView
from gfx.diagram_listing import DiagramListing

class LibrarySearchDockWidget(QDockWidget, Ui_LibrarySearchDockWidget):
    default_root_dir = 'std_lib'

    def __init__(self):
        QDockWidget.__init__(self)
        Ui_LibrarySearchDockWidget.__init__(self)
        self.setupUi(self)
        self._fileTreeView = FileSystemTreeView(self.default_root_dir)
        self.fileSystemLayout.addWidget(self._fileTreeView)
        self.recompileButton.clicked.connect(self.compile_library)
        query_layout = QGridLayout()
        self.queryDiagramTab.setLayout(query_layout)
        self._queryView = QGraphicsView()
        self._queryView.setScene(QueryPreviewCanvas())
        self._queryView.scale(0.6, 0.6)
        query_layout.addWidget(self._queryView)
        self._compilerThread = None
        self._searchThread = None
        self._queryItems = None
        self.searchButton.setEnabled(False)
        self.searchButton.clicked.connect(self.search_library)
    
    def compile_library(self):
        filenames = self._fileTreeView.model().list_all_checked_filenames()
        self._compilerThread = LibraryCompilerThread(filenames)
        self._compilerThread.start()
        self._compilerThread.finished.connect(self.library_compilation_finished)
        
    def library_compilation_finished(self):
        if self._compilerThread.compiled_graph:
            self.searchButton.setEnabled(bool(self._queryItems))            

    def set_items_as_query(self, items, view):
        if items:
            items = list(filter_out_descendents(list(items)))
            self._queryItems = items
            items_copy = pickle.dumps(items)
            items_copy = pickle.loads(items_copy)
            scene = self._queryView.scene()
            scene.clear()
            scene.setBackgroundBrush(view.scene().backgroundBrush())
            rect = QRectF()
            for item in items_copy:
                if isinstance(item, Arrow):
                    item.set_control_points_visible(False)            
                scene.addItem(item)
                rect = rect.united(item.mapToScene(item.boundingRect()).boundingRect())                    
            scene.setSceneRect(rect)
            
            if self._compilerThread and self._compilerThread.compiled_graph:
                self.searchButton.setEnabled(True)
                
            self.tabWidget.setCurrentWidget(self.queryDiagramTab)
        else:
            self._queryItems = None
            self.searchButton.setEnabled(False)
        
    def search_library(self):     
        self.tabWidget.setCurrentWidget(self.searchResultsTab)
        self._searchThread = LibrarySearchThread(self._queryItems, self._compilerThread.compiled_graph)
        self._searchThread.isomorphic_subgraph_match_found.connect(self.subgraph_match_found)
        self._searchThread.run()
        
    def subgraph_match_found(self, match:dict):
        lib_graph = self._searchThread.library_graph
        #query_graph = self._searchThread.query_graph
        
        for lib_node_id in match:
            item = lib_graph.nodes[lib_node_id]['gfxitem']
            diagram_view = item.scene().views()[0]
            self.add_search_result_listing(diagram_view)
            break
        
    def add_search_result_listing(self, view:LanguageGfxView):
        listing = DiagramListing(view)
        self.searchResultsLayout.layout().addWidget(listing)
                           
            
class QueryPreviewCanvas(LanguageCanvas):
    def mousePressEvent(self, event):
        pass
    def mouseReleaseEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass
    def mouseDoubleClickEvent(self, event):
        pass
    def contextMenuEvent(self, event):
        pass