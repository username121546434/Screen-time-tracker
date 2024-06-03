from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem
import csv
from src.constants import APP_NAME_IDX, APP_EXE_IDX


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

        self.update_display()
        self.setLayout(layout)
    
    def update_display(self):
        with open(self.csv_source) as f:
            lines = len(f.readlines())

        self.table.setRowCount(lines)

        with open(self.csv_source) as f:
            reader = csv.reader(f)
            first_line = next(reader)
            total_usage = 0
            usages = []

            for row, line in enumerate(reader):
                app_name = line[APP_NAME_IDX]
                if app_name == 'None':
                    app_name = line[APP_EXE_IDX]
                usage = sum(map(int, line[APP_EXE_IDX + 1:]))

                app_item = QTableWidgetItem(app_name)
                usage_item = QTableWidgetItem(str(usage))

                self.table.setItem(row, 0, app_item)
                self.table.setItem(row, 2, usage_item)

                total_usage += usage
                usages.append(usage)
        
        for row, usage in enumerate(usages):
            percent = int((usage / total_usage) * 100)
            self.table.setItem(row, 1, QTableWidgetItem(f'{percent}%'))
