import datetime
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QItemDelegate
from PySide6.QtCore import QDate, Qt
import csv
from constants import APP_NAME_IDX, APP_EXE_IDX, DATE_FMT, TimePeriod
import re

SECONDS_TYPE = QTableWidgetItem.ItemType.UserType
USAGE_ROLE = Qt.ItemDataRole.UserRole
PERCENT_ROLE = Qt.ItemDataRole.UserRole + 1
PERCENT_TYPE = QTableWidgetItem.ItemType.UserType + 1

def format_seconds(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:>3}h {minutes:>3}m {seconds:>3}s"


def unformat_seconds(time_string: str):
    # Define regex patterns for hours, minutes, and seconds
    hours_pattern = r'(\d+)h'
    minutes_pattern = r'(\d+)m'
    seconds_pattern = r'(\d+)s'
    
    # Find all matches in the string
    hours_match = re.search(hours_pattern, time_string)
    minutes_match = re.search(minutes_pattern, time_string)
    seconds_match = re.search(seconds_pattern, time_string)
    
    # Extract the values or default to 0 if not found
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0

    minutes += hours * 60
    seconds += minutes * 60
    
    return seconds


class ItemDelegate(QItemDelegate):
    def __init__(self, parent, table: QTableWidget):
        super(ItemDelegate, self).__init__(parent)
        self.table = table

    def paint(self, painter, option, index):
        item = self.table.itemFromIndex(index)
        # This ensures the table is always displaying
        # the int/float value stored in the custom data role.
        if item.text() != str(item.data(USAGE_ROLE)) and item.data(USAGE_ROLE) is not None:
            item.setText(format_seconds(item.data(USAGE_ROLE)))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        elif item.data(PERCENT_ROLE) is not None:
            item.setText(f'{item.data(PERCENT_ROLE):.2%}')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        super(ItemDelegate, self).paint(painter, option, index)


class UsageItem(QTableWidgetItem):
    def __init__(self, usage: int, *args, **kw):
        self.usage = usage
        super().__init__(*args, **kw)
    
    def __lt__(self, other):
        if isinstance(other, UsageItem):
            return self.usage < other.usage
        raise ValueError


class AppsDisplay(QWidget):
    def __init__(self, csv_file: Path | str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.csv_source = csv_file
        layout = QHBoxLayout(self)

        self.table = table = QTableWidget(self)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

        self.delegate = ItemDelegate(self, self.table)
        self.table.setItemDelegate(self.delegate)

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
        self.table.setSortingEnabled(False)
        # sorting breaks the table sometimes
        # when setting items in a loop

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

                app_item = QTableWidgetItem(app_name)
                usage_item = UsageItem(usage, SECONDS_TYPE)

                usage_item.setData(USAGE_ROLE, usage)

                self.table.setItem(row, 0, app_item)
                self.table.setItem(row, 2, usage_item)

                total_usage += usage
                usages.append(usage)
        
        for row, usage in enumerate(usages):
            item = QTableWidgetItem(PERCENT_TYPE)
            item.setData(PERCENT_ROLE, usage/total_usage)
            self.table.setItem(row, 1, item)

        self.table.setSortingEnabled(True)
