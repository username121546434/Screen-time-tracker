from get_process import get_active_window_app_name, get_active_window_app_path, get_app_name_from_exe
import time
from datetime import datetime
from constants import FILE, DATE_FMT_SQL, TABLE_NAME, APP_EXE_COL, APP_NAME_COL
import sqlite3

database = sqlite3.connect(FILE)
cursor = database.cursor()
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    {APP_EXE_COL} text,
    {APP_NAME_COL} text,
    {datetime.now().strftime(DATE_FMT_SQL)} INT default 0,
    PRIMARY KEY ({APP_EXE_COL}, {APP_NAME_COL})
);
""")
updates = 0


def add_program(name: str, exe: str):
    cursor.execute(f"""
INSERT INTO {TABLE_NAME} ({APP_NAME_COL}, {APP_EXE_COL}, {datetime.now().strftime(DATE_FMT_SQL)})
VALUES (?,?,?)
""", (name, exe, 1))
    database.commit()
    return cursor.lastrowid


def program_exists(name: str, exe: str):
    cursor.execute(f"""
SELECT count(*)
FROM {TABLE_NAME}
WHERE (({APP_NAME_COL} = ?) AND ({APP_EXE_COL} = ?))
""", (name, exe))
    data = cursor.fetchone()
    return data[0] != 0


def increment_program(name: str, exe: str):
    column = datetime.now().strftime(DATE_FMT_SQL)
    cursor.execute(f"""
UPDATE {TABLE_NAME}
SET {column} = {column} + 1
WHERE ({APP_NAME_COL} = ?) AND ({APP_EXE_COL} = ?)
""", (name, exe))
    database.commit()


def write_data(proc_name: str | None, app_name: str | None):
    if proc_name is None or app_name == '':
        return
    try:
        cursor.execute("ALTER TABLE " + TABLE_NAME + " ADD COLUMN " + \
                    datetime.now().strftime(DATE_FMT_SQL) + \
                    " INTEGER default 0")
    except sqlite3.OperationalError as e:
        print(e)

    if not program_exists(app_name, proc_name):
        print("New program added", app_name)
        add_program(app_name, proc_name)
        return
    
    increment_program(app_name, proc_name)


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
