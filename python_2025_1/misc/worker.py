# import glob
from typing import Optional, Any

from dataclasses import dataclass
from enum import Enum
import os
import re
from pathlib import Path
from datetime import date, datetime
import gzip
import sys
import logging

import polars as pl
import pandas as pd


# from python_2025_1.misc.html_template import html_template
sys.path.insert(1, str(Path(__file__).parent.parent.parent.resolve()))
from python_2025_1.misc.html_template import html_template
from python_2025_1.misc.misc import FileType, Log, PrettyPrintDict

# from html_template import html_template
# from misc import FileType, Log, PrettyPrintDict


# class FileType(Enum):
#     Unknown = 0
#     Gz = 1
#     Text = 2
#
#
# @dataclass
# class Log:
#     path: Path
#     file_type: FileType
#
#     def get_date(self) -> Optional[date]:
#         if self.file_type == FileType.Gz:
#             return datetime.strptime(str(self.path)[-11:-3], "%Y%m%d").date()
#         elif self.file_type == FileType.Text:
#             return datetime.strptime(str(self.path)[-8:], "%Y%m%d").date()
#         else:
#             return None
#
#
# class PrettyPrintDict(dict):
#
#     def __repr__(self) -> str:
#         d = {k: round(v, 3) if isinstance(v, float) else v for k,v in self.items()}
#         # print(d)
#         return str(d)


class Worker:

    def __init__(self, log_dir: str, report_dir: str, logger: logging.Logger):
        self.log_dir = log_dir
        self.report_dir = report_dir
        self.logger = logger

    @staticmethod
    def log_type(f: str) -> FileType:
        if re.match(r"nginx-access-ui\.log-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\.gz", f):
            return FileType.Gz
        elif re.match(r"nginx-access-ui\.log-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", f):
            return FileType.Text
        return FileType.Unknown

    def get_log(self) -> Log:
        self.logger.info("searching for log...")
        logs : list[Log] = [
            Log(path=Path.joinpath(Path(self.log_dir), f).resolve(), file_type=Worker.log_type(f))
            for f in os.listdir(self.log_dir) if Worker.log_type(f) != FileType.Unknown
        ]
        l = max(logs, key=lambda x: x.get_date())
        self.logger.info(f"found log={l}")
        return l

    @staticmethod
    def url_of_request(r: str) -> Optional[str]:
        li = r.split(" ")
        if len(li) > 1:
            return li[1]
        else:
            return None

    def get_log_stats(self, log: Log) -> list[PrettyPrintDict[str, Any]]:
        self.logger.info(f"processing log={log}...")

        if log.file_type == FileType.Gz:
            f = gzip.open(log.path, "rb")
        elif log.file_type == FileType.Text:
            f = open(log.path, "rb")
        else:
            s = f"unknown log file type={log}"
            self.logger.error(s)
            raise Exception(s)
        # with gzip.open(log.path, "rb") as f:
            # df = pl.read_csv(
            #     f,
            #     separator=" ",
            #     has_header=False,
            #     # columns=[
            #     #     "remote_addr",
            #     #     "remote_user",
            #     #     "http_x_real_ip",
            #     #     "time_local",
            #     #     "request",
            #     #     "status",
            #     #     "body_bytes_sent",
            #     #     "http_referer",
            #     #     "http_user_agent",
            #     #     "http_x_forwarded_for",
            #     #     "http_X_Request_id",
            #     #     "http_x_rb_user",
            #     #     "request_time",
            #     # ],
            # )

            # df = pl.from_pandas(
            #     dd.read_csv(f, delim_whitespace=True, header=None).compute()
            # )
        df = pd.read_csv(
            f,
            header=None,
            sep=r"\s+",
            names=[
                "remote_addr",
                "remote_user",
                "http_x_real_ip",
                "time_wo_timezone_local",
                "timezone_local",
                "request",
                "status",
                "body_bytes_sent",
                "http_referer",
                "http_user_agent",
                "http_x_forwarded_for",
                "http_X_Request_id",
                "http_x_rb_user",
                "request_time",
            ],
        )

        df["url"] = df.apply(lambda x: Worker.url_of_request(x["request"]), axis=1)
        # print(df.iloc[0])

        df2 = pl.DataFrame(df[["url", "request_time"]])
        totals = pl.sql("""
            select count(*) as total_count
                ,sum(request_time) as total_time_sum
            from df2
        """).collect().to_dicts()[0] #to_dict(as_series=False)
        # print(f"totals={totals}")

        # df2 = pl.sql("""
        # with t as (
        #     select count(*) as total_count
        #         ,sum(request_time) as total_time_sum
        #     from df2
        # ), t2 as (
        #     select url
        #         ,count(*) as count
        #         ,avg(request_time) as time_avg
        #         ,max(request_time) as time_max
        #         ,median(request_time) as time_med
        #         ,sum(request_time) as time_sum
        #     from df2
        #     group by url
        # )
        # select t2.url
        #     ,t2.count
        #     ,cast(t2.count as float) / t.total_count as count_perc
        #     ,t2.time_avg
        #     ,t2.time_max
        #     ,t2.time_med
        #     ,t2.time_sum / t.total_time_sum as time_perc
        #     ,t2.time_sum
        # from t2
        # cross join t
        # order by 2 desc
        # limit 100
        # """).collect()

        df2 = pl.sql(f"""
            select url
                ,count(*) as count
                ,cast(count(*) as float) / {totals["total_count"]} as count_perc
                ,avg(request_time) as time_avg
                ,max(request_time) as time_max
                ,median(request_time) as time_med
                ,sum(request_time) / {totals["total_time_sum"]} as time_perc
                ,sum(request_time) as time_sum
            from df2
            group by url
            order by 2 desc
            limit 100
        """).collect()
        # print(df2)
        # print(df2.height)

        res = [PrettyPrintDict(x) for x in df2.to_dicts()]
        # print(f"type(res[0]) = {type(res[0])}")
        self.logger.info("log processed")
        return res

    def generate_report(self, log: Log, table: list[PrettyPrintDict[str, Any]]):
        self.logger.info("generating report...")
        html = html_template
        last_row = len(table) - 1
        html = html.replace("___TABLE___", str(table))
        html = html.replace("___LAST_ROW___", str(last_row))

        outfile = log.get_date().strftime("report-%Y.%m.%d.html")
        report_path = Path.joinpath(Path(self.report_dir), outfile).resolve()
        try:
            with open(report_path, "w") as f:
                f.write(html)
            self.logger.info("report created")
        except Exception as e:
            self.logger.error(str(e))
