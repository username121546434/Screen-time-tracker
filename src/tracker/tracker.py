import os
from .get_process import get_active_window_app_name, get_active_window_app_path, get_app_name_from_exe
import time
from datetime import datetime
import csv
from constants import FILE, DATE_FMT, APP_EXE_IDX, APP_NAME_IDX
from tempfile import TemporaryFile


def write_data(proc_name: str | None, app_name: str | None):
    if proc_name is None or app_name == '':
        return
    if app_name is None:
        app_name = str(app_name)

    date = datetime.now().strftime(DATE_FMT)
    with open(FILE, newline='') as f, TemporaryFile('w', newline='', delete=False) as tmp:
        reader = csv.reader(f)
        writer = csv.writer(tmp)

        first_line = next(reader)
        found_program = False
        missing_date = False
    
        if date not in first_line:
            first_line.append(date)
            missing_date = True
        date_idx = first_line.index(date)
        writer.writerow(first_line)
        
        for line in reader:
            if missing_date:
                line.append('0')
            if line[APP_EXE_IDX] == proc_name and line[APP_NAME_IDX] == app_name:
                line[date_idx] = str(int(line[date_idx]) + 1)
                found_program = True
            writer.writerow(line)

        if not found_program:
            newline = [app_name, proc_name]
            newline.extend(['0'] * (date_idx - 2))
            newline.append('1')
            writer.writerow(newline)

    # with open(tmp.name) as f, open(FILE, 'w') as w:
    #     w.write(f.read())

    os.replace(tmp.name, FILE)


def track():
    filename, fullpath = get_active_window_app_name(), get_active_window_app_path()
    name = get_app_name_from_exe(fullpath)
    write_data(filename, name)
    return name, filename


def main():
    while True:
        time.sleep(1)
        print(track())


if __name__ == '__main__':
    main()
