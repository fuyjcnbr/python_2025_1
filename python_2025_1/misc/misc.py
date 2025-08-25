# import glob
from typing import Optional, Any

from dataclasses import dataclass
from enum import Enum
import os
import re
from pathlib import Path
from datetime import date, datetime
# import gzip
# import sys
#
# import polars as pl
# import pandas as pd


# from python_2025_1.misc.html_template import html_template
# import html_template


class FileType(Enum):
    Unknown = 0
    Gz = 1
    Text = 2


@dataclass
class Log:
    path: Path
    file_type: FileType

    def get_date(self) -> Optional[date]:
        if self.file_type == FileType.Gz:
            return datetime.strptime(str(self.path)[-11:-3], "%Y%m%d").date()
        elif self.file_type == FileType.Text:
            return datetime.strptime(str(self.path)[-8:], "%Y%m%d").date()
        else:
            return None


class PrettyPrintDict(dict):

    def __repr__(self) -> str:
        d = {k: round(v, 3) if isinstance(v, float) else v for k,v in self.items()}
        # print(d)
        return str(d)