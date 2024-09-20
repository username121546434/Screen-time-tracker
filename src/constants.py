from pathlib import Path
from typing import Literal

DATE_FMT = r'%d-%m-%Y'
DATE_FMT_SQL = r'date_%d_%m_%Y'
FILE = Path('data.db').resolve()

TABLE_NAME = 'Data'
APP_NAME_COL = 'AppName'
APP_EXE_COL = 'AppExe'

APP_NAME_IDX = 1
APP_EXE_IDX = 0

TimePeriod = Literal['Day', 'Month', 'Year', 'All Time']