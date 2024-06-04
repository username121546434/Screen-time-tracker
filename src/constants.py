from pathlib import Path
from typing import Literal

DATE_FMT = r'%d-%m-%Y'
FILE = Path('data.csv').resolve()
APP_EXE_IDX = 1
APP_NAME_IDX = 0

TimePeriod = Literal['Day', 'Month', 'Year', 'All Time']