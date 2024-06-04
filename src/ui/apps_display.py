import datetime
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate
import csv
from constants import APP_NAME_IDX, APP_EXE_IDX, DATE_FMT, TimePeriod


def format_seconds(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h {minutes}m {seconds}s"


class AppsDisplay(QWidget):
    def __init__(self, csv_file: Path | str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.csv_source = csv_file
        layout = QHBoxLayout(self)

        self.table = table = QTableWidget(self)
        layout.addWidget(self.table)

        with open(csv_file) as f:
            lines = len(f.readlines())

        table.setColumnCount(3)
        table.setRowCount(lines)
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 49)
        table.setColumnWidth(2, 48)
        table.setHorizontalHeaderLabels(['Name', 'Percent', 'Usage'])

        self.update_display(QDate(), 'All Time')
        self.setLayout(layout)
    
    def update_display(self, date: QDate, time: TimePeriod):
        with open(self.csv_source) as f:
            lines = len(f.readlines())

        self.table.setRowCount(lines)

        with open(self.csv_source) as f:
            reader = csv.reader(f)
            total_usage = 0
            usages = []
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

                app_item = QTableWidgetItem(app_name)
                usage_item = QTableWidgetItem(format_seconds(usage))

                self.table.setItem(row, 0, app_item)
                self.table.setItem(row, 2, usage_item)

                total_usage += usage
                usages.append(usage)
        
        for row, usage in enumerate(usages):
            self.table.setItem(row, 1, QTableWidgetItem(f'{(usage/total_usage):.2%}'))
