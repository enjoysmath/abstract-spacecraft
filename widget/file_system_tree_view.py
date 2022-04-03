from PyQt5.QtWidgets import QFileSystemModel, QTreeView,QStyledItemDelegate
from PyQt5.QtCore import QFileSystemWatcher, QModelIndex, Qt
import os
from core.checkable_file_system_model import CheckableFileSystemModel

class FileSystemTreeView(QTreeView):
    def __init__(self, root_dir:str=None):
        super().__init__()
        if root_dir is None:
            root_dir = os.getcwd()
        root_dir = os.path.abspath(root_dir)
        self._rootDir = None
        self.file_sys_model = CheckableFileSystemModel()
        index = self.file_sys_model.setRootPath(root_dir)
        self._watcher = None
        self.set_root_dir(root_dir)
        self.setModel(self.file_sys_model)
        self.setRootIndex(index)

    def set_root_dir(self, root_dir:str):
        if self._watcher is not None:
            self._watcher.fileChanged.disconnect(self.file_changed)
            del self._watcher
        self._watcher = QFileSystemWatcher()
        self._watcher.fileChanged.connect(self.file_changed)
        self._watcher.addPath(root_dir)
        self._rootDir = root_dir

    def file_changed(self, filepath:str):
        print('TODO fliechanged', filepath)