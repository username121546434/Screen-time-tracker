import sqlite3
from constants import TimePeriod, TABLE_NAME, DATE_FMT_SQL, APP_NAME_IDX, APP_EXE_IDX
from datetime import datetime
from PySide6.QtCore import QDate


def get_data(cursor: sqlite3.Cursor, date: QDate, time_period: TimePeriod, include_other: bool = False):
    lst: list[tuple[str, int]] = []
    total = 0
    cursor.execute(f"select * from {TABLE_NAME}")

    data = cursor.fetchall()
    columns = {datetime.strptime(i[0], DATE_FMT_SQL): APP_NAME_IDX + idx + 1
               for idx, i in enumerate(cursor.description[APP_NAME_IDX + 1:])}
    print(data)
    print(columns)

    for row, row_data in enumerate(data):
        app_name: str = row_data[APP_NAME_IDX]
        if app_name == "None":
            app_name = row_data[APP_EXE_IDX]

        if time_period == 'All Time':
            usage = sum(map(int, row_data[APP_NAME_IDX + 1:]))
        elif time_period == 'Day':
            day = date.toPython() # this returns a datetime.date object
            day = datetime(day.year, day.month, day.day)
            idx = columns[day]
            usage = int(row_data[idx])
        elif time_period == 'Month':
            month = date.month()
            year = date.year()
            usage = 0
            for day in range(1, 32):
                try:
                    day = datetime(year, month, day)
                    idx = columns[day]
                except KeyError:
                    pass
                except ValueError:
                    break
                else:
                    usage += int(row_data[idx])
        elif time_period == 'Year':
            year = date.year()
            usage = 0
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        day = datetime(year, month, day)
                        idx = columns[day]
                    except (KeyError, ValueError):
                        pass
                    else:
                        usage += int(row_data[idx])

        total += usage

        lst.append((app_name, usage))

    lst.sort(key=lambda a: a[1], reverse=True)

    if include_other:
        new_lst: list[tuple[str, int]] = []
        other_usage = 0
        for app, usage in lst:
            if usage / total < 0.01:
                other_usage += usage
            else:
                new_lst.append((app, usage))
        new_lst.append(("Other", other_usage))
        lst = new_lst

    return lst, total
