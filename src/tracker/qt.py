from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import time
from .tracker import track


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
        while True:
            time.sleep(1)
            if getattr(self, 'quit', False):
                return
            name = track()
            print(name)
            self.signals.finished.emit(name)

    def stop(self):
        self.quit = True
