from datetime import datetime
import os
from pathlib import Path
import sys
from typing import Literal
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QIcon, QCloseEvent, QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QPushButton
from constants import DATE_FMT, FILE
from ui.apps_display import AppsDisplay
from ui.pie_chart import ScreenTimeChart
from ui.date_input import DateInput
from ui.bar_graph import ScreenTimeBarGraph
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

        self.date.date.dateChanged.connect(self.update)
        self.date.time_period.currentTextChanged.connect(self.update)

        self.chart = ScreenTimeChart(self)
        layout.addWidget(self.chart.chart_view)

        self.bar_graph = ScreenTimeBarGraph(self)
        layout.addWidget(self.bar_graph.chart_view)
        self.bar_graph.chart_view.hide()

        self.current_graph_displayed: Literal['Pie', 'Bar'] = 'Pie'

        self.switch_button = QPushButton("Switch between bar graph and pie chart")
        self.switch_button.clicked.connect(self.switch_graph)
        layout.addWidget(self.switch_button)

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
    
    def switch_graph(self):
        print("Switch graph called", f'{self.current_graph_displayed = }')
        if self.current_graph_displayed == 'Pie':
            self.chart.chart_view.hide()
            self.bar_graph.chart_view.show()
            self.current_graph_displayed = 'Bar'
        else:
            self.bar_graph.chart_view.hide()
            self.chart.chart_view.show()
            self.current_graph_displayed = 'Pie'

    def on_update(self, name: tuple[str, str]):
        if self.isHidden():
            return
        self.label.setText(f'Current App: {name}')

    def update(self):
        try:
            self.apps.update_display(self.date.date.date(), self.date.time_period.currentText())
            self.chart.update(self.date.date.date(), self.date.time_period.currentText())
            self.bar_graph.update(self.date.date.date(), self.date.time_period.currentText())
        except KeyError:
            self.statusBar().showMessage(f'No data for {self.date.date.date().toPython()}', 2000)
            raise
    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.hide()


def main():
    database = sqlite3.connect(FILE)
    cursor = database.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {APP_EXE_COL} text,
        {APP_NAME_COL} text,
        {datetime.now().strftime(DATE_FMT_SQL)} INT default 0,
        PRIMARY KEY ({APP_EXE_COL}, {APP_NAME_COL})
    );
    """)
    database.commit()

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

