import csv
from datetime import datetime
from constants import APP_EXE_IDX, APP_NAME_IDX, DATE_FMT, FILE, TimePeriod
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtCore import QDate
from get_data import get_data


class ScreenTimeChart(QPieSeries):
    def __init__(self, parent):
        super().__init__(parent)
        self.csv_source = FILE

        self._chart = QChart()
        self._chart.addSeries(self)
        self._chart.legend().hide()
        self._chart.setMinimumSize(500, 400)

        self.hovered.connect(self.hovered_over)

        self.chart_view = QChartView(self._chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.update(QDate(), 'All Time')
    
    def update(self, date: QDate, time: TimePeriod):
        self.clear()

        if time == 'All Time':
            self._chart.setTitle('All Time Screen Time')
        elif time == 'Day':
            day = date.toPython() # this returns a datetime.date object
            day = datetime(day.year, day.month, day.day)
            self._chart.setTitle(f'Screen time for {day:{DATE_FMT}}')
        elif time == 'Month':
            self._chart.setTitle(f'Screen time for {datetime(date.year(), date.month(), date.day()-1):%B %Y}')
        elif time == 'Year':
            self._chart.setTitle(f'Screen time for {date.year()}')

        lst, total = get_data(self.csv_source, date, time)

        for i in lst:
            self.append(f'{i[0]} {(i[1] / total):.1%}', i[1])
    
    def hovered_over(self, slice: QPieSlice, state: bool):
        slice.setExploded(state)
        slice.setLabelVisible(state)
