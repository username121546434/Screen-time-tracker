from datetime import datetime
import os
from pathlib import Path
import sys
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QIcon, QCloseEvent, QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QPushButton
from constants import DATE_FMT, FILE
from ui.apps_display import AppsDisplay
from ui.pie_chart import ScreenTimeChart
from ui.date_input import DateInput
from tracker.qt import TrackerWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setWindowTitle('Screen Time Tracker')
        self.setMinimumSize(300, 450)

        layout = QVBoxLayout()

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.date = DateInput()
        layout.addWidget(self.date)

        self.chart = ScreenTimeChart(self)
        layout.addWidget(self.chart.chart_view)

        self.label = QLabel(self)
        layout.addWidget(self.label)
        
        self.refresh = QPushButton("Refresh", self)
        layout.addWidget(self.refresh)
        self.refresh.clicked.connect(self.update)

        self.apps = AppsDisplay(FILE, self)
        layout.addWidget(self.apps)

        self.threadpool = QThreadPool()
        self.worker = TrackerWorker()
        self.worker.signals.finished.connect(self.on_update)
        self.threadpool.start(self.worker)

    def on_update(self, name: tuple[str, str]):
        if self.isHidden():
            return
        self.label.setText(f'Current App: {name}')

    def update(self):
        self.apps.update_display()
        self.chart.update()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.hide()


def main():
    if not os.path.exists(FILE):
        with open(FILE, 'w') as f:
            f.write(f'AppName,ExeName,{datetime.now():{DATE_FMT}}')

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()

    icon = QIcon(str(Path("clock.png").resolve()))

    tray = QSystemTrayIcon(icon)
    tray.setVisible(True)

    menu = QMenu()

    open_action = QAction('Open')
    open_action.triggered.connect(window.show)
    menu.addAction(open_action)

    quit_action = QAction('Quit')
    # sys.exit is a failsafe incase somehow app.quit() doesn't work
    quit_action.triggered.connect(lambda: (window.worker.signals.stop.emit(), app.quit(), sys.exit()))
    menu.addAction(quit_action)

    window.show()

    tray.setContextMenu(menu)
    app.exec()


if __name__ == '__main__':
    main()

