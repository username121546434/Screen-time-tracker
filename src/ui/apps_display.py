import datetime
from datetime import datetime
import sqlite3
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QItemDelegate, QHeaderView
from PySide6.QtCore import QDate, Qt
import csv
from constants import DATE_FMT, TimePeriod
from .get_data import get_data
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
        if item and item.text() != str(item.data(USAGE_ROLE)) and item.data(USAGE_ROLE) is not None:
            item.setText(format_seconds(item.data(USAGE_ROLE)))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        elif item and item.data(PERCENT_ROLE) is not None:
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
    def __init__(self, cursor: sqlite3.Cursor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.table = table = QTableWidget(self)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

        self.delegate = ItemDelegate(self, self.table)
        self.table.setItemDelegate(self.delegate)

        layout.addWidget(self.table)

        table.setColumnCount(3)
        table.horizontalHeader().setMinimumWidth(150)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.setHorizontalHeaderLabels(['Name', 'Percent', 'Usage'])

        self.update_display(QDate(), 'All Time', cursor)
        self.setLayout(layout)
    
    def update_display(self, date: QDate, time: TimePeriod, cursor: sqlite3.Cursor):
        self.table.setSortingEnabled(False)
        # sorting breaks the table sometimes
        # when setting items in a loop


        data = get_data(cursor, date, time)
        total_usage = data[1]
        self.table.setRowCount(len(data[0]) + 1)
        
        for row, (app_name, usage) in enumerate(data[0]):
            app_item = QTableWidgetItem(app_name)
            usage_item = UsageItem(usage, SECONDS_TYPE)

            usage_item.setData(USAGE_ROLE, usage)

            self.table.setItem(row, 0, app_item)
            self.table.setItem(row, 2, usage_item)

            item = QTableWidgetItem(PERCENT_TYPE)
            item.setData(PERCENT_ROLE, usage/total_usage)
            self.table.setItem(row, 1, item)
        

        self.table.setSortingEnabled(True)
