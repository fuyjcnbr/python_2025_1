from pathlib import Path
from datetime import date

from python_2025_1.misc.misc import Log, FileType


def test_log_get_date_gz():
    l = Log(path=Path("nginx-access-ui.log-20170630.gz"), file_type=FileType.Gz)
    assert(l.get_date() == date(year=2017, month=6, day=30))

def test_log_get_date_text():
    l = Log(path=Path("nginx-access-ui.log-20170630"), file_type=FileType.Text)
    assert(l.get_date() == date(year=2017, month=6, day=30))
