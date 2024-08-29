from constants import FILE, TimePeriod
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import QChart, QChartView, QHorizontalBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtCore import QDate, Qt
from .get_data import get_data
from .get_title import get_title
from .apps_display import format_seconds

DEFAULT_COLOR = QColor.fromHsvF(0.555833, 0.000000, 1.000000, 1.000000)


class ScreenTimeBarGraph(QHorizontalBarSeries):
    def __init__(self, parent):
        super().__init__(parent)
        self.csv_source = FILE

        self._chart = QChart()
        self._chart.addSeries(self)
        self._chart.setMinimumSize(400, 400)
        self.setLabelsVisible(True)
        self.setLabelsFormat('@value hours')
        self.setLabelsPrecision(2)

        self.hovered.connect(self.hovered_over)

        self.x_axis = axis_x = QBarCategoryAxis()
        self._chart.addAxis(axis_x, Qt.AlignmentFlag.AlignLeft)
        self.attachAxis(axis_x)

        self.y_axis = axis_y = QValueAxis()
        self.update(QDate(), 'All Time')
        axis_y.setTickCount(7)
        axis_y.setLabelFormat(r"%dh")
        self._chart.addAxis(axis_y, Qt.AlignmentFlag.AlignBottom)
        self.attachAxis(axis_y)

        self.chart_view = QChartView(self._chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
    
    def hovered_over(self, bool_val: bool, int_val: int, q_set: QBarSet):
        print(bool_val, int_val, q_set, q_set.label(), q_set)

        if bool_val:
            q_set.setBorderColor('red')
        else:
            q_set.setBorderColor(DEFAULT_COLOR)
    
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
            set_.setLabel(f'{app} {format_seconds(int(usage * 3600))}')
            self.append(set_)


        self.y_axis.setRange(0, max(usages))
