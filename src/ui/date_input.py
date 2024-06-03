from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDateEdit, QComboBox
from datetime import datetime


class DateInput(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()

        now = datetime.now()
        self.date = QDateEdit(QDate(now.year, now.month, now.day))
        layout.addWidget(self.date)

        self.time_period = QComboBox()
        self.time_period.addItems(['Day', 'Month', 'Year', 'All Time'])
        self.time_period.setCurrentIndex(3)
        layout.addWidget(self.time_period)

        self.setLayout(layout)
