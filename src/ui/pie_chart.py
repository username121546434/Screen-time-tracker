import csv
from datetime import datetime
from constants import APP_EXE_IDX, APP_NAME_IDX, DATE_FMT, FILE, TimePeriod
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
    
    def update(self, date: QDate, time: TimePeriod):
        self.clear()
        lst = []
        total = 0
        with open(self.csv_source) as f:
            reader = csv.reader(f)
            first_line = {}
            for idx, i in enumerate(next(reader)):
                try:
                    first_line[datetime.strptime(i, DATE_FMT)] = idx
                except ValueError:
                    pass

            for row, line in enumerate(reader):
                app_name = line[APP_NAME_IDX]
                if app_name == 'None':
                    app_name = line[APP_EXE_IDX]
                
                if time == 'All Time':
                    usage = sum(map(int, line[APP_EXE_IDX + 1:]))
                elif time == 'Day':
                    day = date.toPython() # this returns a datetime.date object
                    day = datetime(day.year, day.month, day.day)
                    idx = first_line[day]
                    usage = int(line[idx])
                elif time == 'Month':
                    month = date.month()
                    year = datetime.now().year
                    usage = 0
                    for day in range(1, 32):
                        try:
                            day = datetime(year, month, day)
                            idx = first_line[day]
                        except (KeyError, ValueError):
                            pass
                        else:
                            usage += int(line[idx])
                elif time == 'Year':
                    year = date.year()
                    usage = 0
                    for month in range(1, 13):
                        for day in range(1, 32):
                            try:
                                day = datetime(year, month, day)
                                idx = first_line[day]
                            except (KeyError, ValueError):
                                pass
                            else:
                                usage += int(line[idx])

                total += usage

                lst.append((app_name, usage))

        lst.sort(key=lambda a: a[1], reverse=True)
        for i in lst:
            self.append(f'{i[0]} {(i[1] / total):.1%}', i[1])
    
    def hovered_over(self, slice: QPieSlice, state: bool):
        slice.setExploded(state)
        slice.setLabelVisible(state)
