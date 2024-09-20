from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import time
from .tracker import track
import sqlite3
from constants import FILE


class TrackerSignals(QObject):
    finished = Signal(tuple)
    stop = Signal()


class TrackerWorker(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = TrackerSignals()
        self.signals.stop.connect(self.stop)
    
    @Slot()
    def run(self) -> None:
        database = sqlite3.connect(FILE)
        cursor = database.cursor()
        while True:
            time.sleep(1)
            if getattr(self, 'quit', False):
                return
            name = track(cursor)
            print(name)
            self.signals.finished.emit(name)

    def stop(self):
        self.quit = True
