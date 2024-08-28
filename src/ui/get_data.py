import csv
from constants import TimePeriod, DATE_FMT, APP_EXE_IDX, APP_NAME_IDX
from datetime import datetime
from PySide6.QtCore import QDate


def get_data(csv_file: str, date: QDate, time_period: TimePeriod):
    lst: list[tuple[str, int]] = []
    total = 0
    with open(csv_file) as f:
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
            
            if time_period == 'All Time':
                usage = sum(map(int, line[APP_EXE_IDX + 1:]))
            elif time_period == 'Day':
                day = date.toPython() # this returns a datetime.date object
                day = datetime(day.year, day.month, day.day)
                idx = first_line[day]
                usage = int(line[idx])
            elif time_period == 'Month':
                month = date.month()
                year = date.year()
                usage = 0
                for day in range(1, 32):
                    try:
                        day = datetime(year, month, day)
                        idx = first_line[day]
                    except KeyError:
                        pass
                    except ValueError:
                        break
                    else:
                        usage += int(line[idx])
            elif time_period == 'Year':
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
    return lst, total