import csv
from constants import APP_EXE_IDX, APP_NAME_IDX, FILE, TimePeriod
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtCore import QDate


class ScreenTimeChart(QPieSeries):
    def __init__(self, parent):
        super().__init__(parent)
        self.csv_source = FILE
        self.update(QDate(), 'All Time')

        self._chart = QChart()
        self._chart.addSeries(self)
        self._chart.legend().hide()
        self._chart.setMinimumSize(400, 200)

        self.hovered.connect(self.hovered_over)

        self.chart_view = QChartView(self._chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
    
    def update(self, date: QDate, time_period: TimePeriod):
        self.clear()
        lst = []
        total = 0
        with open(self.csv_source) as f:
            reader = csv.reader(f)
            first_line = next(reader)

            for row, line in enumerate(reader):
                app_name = line[APP_NAME_IDX]
                if app_name == 'None':
                    app_name = line[APP_EXE_IDX]
                usage = sum(map(int, line[APP_EXE_IDX + 1:]))
                total += usage

                lst.append((app_name, usage))

        lst.sort(key=lambda a: a[1], reverse=True)
        for i in lst:
            self.append(f'{i[0]} {(i[1] / total):.1%}', i[1])
    
    def hovered_over(self, slice: QPieSlice, state: bool):
        slice.setExploded(state)
        slice.setLabelVisible(state)
