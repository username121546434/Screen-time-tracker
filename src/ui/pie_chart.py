from constants import FILE, TimePeriod
import sqlite3
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtCore import QDate
from .get_data import get_data
from .get_title import get_title


class ScreenTimeChart(QPieSeries):
    def __init__(self, parent, cursor: sqlite3.Cursor):
        super().__init__(parent)

        self._chart = QChart()
        self._chart.addSeries(self)
        self._chart.legend().hide()
        self._chart.setMinimumSize(500, 400)

        self.hovered.connect(self.hovered_over)

        self.chart_view = QChartView(self._chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.update(QDate(), 'All Time', cursor)
    
    def update(self, date: QDate, time: TimePeriod, cursor: sqlite3.Cursor):
        self.clear()

        self._chart.setTitle(get_title(time, date))

        lst, total = get_data(cursor, date, time)

        for i in lst:
            self.append(f'{i[0]} {(i[1] / total):.1%}', i[1])
    
    def hovered_over(self, slice: QPieSlice, state: bool):
        slice.setExploded(state)
        slice.setLabelVisible(state)
