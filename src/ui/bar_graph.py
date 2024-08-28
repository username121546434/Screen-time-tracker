import csv
from datetime import datetime
from constants import APP_EXE_IDX, APP_NAME_IDX, DATE_FMT, FILE, TimePeriod
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QHorizontalBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtCore import QDate, Qt
from .get_data import get_data
from .get_title import get_title


class ScreenTimeBarGraph(QHorizontalBarSeries):
    def __init__(self, parent):
        super().__init__(parent)
        self.csv_source = FILE

        self._chart = QChart()
        self._chart.addSeries(self)
        self._chart.setMinimumSize(400, 400)

        # self.hovered.connect(self.hovered_over)

        self.x_axis = axis_x = QBarCategoryAxis()
        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignLeft)
        self.attachAxis(axis_x)

        self.y_axis = axis_y = QValueAxis()
        self.update(QDate(), 'All Time')
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignBottom)
        self.attachAxis(axis_y)

        self.chart_view = QChartView(self._chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
    
    def update(self, date: QDate, time_period: TimePeriod):
        self.clear()

        self._chart.setTitle(get_title(time_period, date))

        lst, total = get_data(self.csv_source, date, time_period, include_other=True)
        lst = lst[::-1]

        usages: list[int] = []

        for app, usage in lst:
            usage = usage / 3600    # 3600 is the number of seconds in an hour
            usages.append(usage)

            set_ = QBarSet(app)
            set_.append(usage)
            self.append(set_)


        self.y_axis.setRange(0, max(usages))
