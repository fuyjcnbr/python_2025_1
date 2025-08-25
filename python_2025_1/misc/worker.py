from typing import Optional, Any
import os
import re
from pathlib import Path
import gzip
import sys
import logging

import polars as pl
import pandas as pd


sys.path.insert(1, str(Path(__file__).parent.parent.parent.resolve()))
from python_2025_1.misc.html_template import html_template
from python_2025_1.misc.misc import FileType, Log, PrettyPrintDict


class Worker:

    def __init__(self, log_dir: str, report_dir: str, logger: logging.Logger, report_size: int):
        self.log_dir = log_dir
        self.report_dir = report_dir
        self.logger = logger
        self.report_size = report_size

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
        log = max(logs, key=lambda x: x.get_date())
        self.logger.info(f"found log={log}")
        return log

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

        df2 = pl.DataFrame(df[["url", "request_time"]])
        totals = pl.sql("""
            select count(*) as total_count
                ,sum(request_time) as total_time_sum
            from df2
        """).collect().to_dicts()[0] #to_dict(as_series=False)

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
            limit {self.report_size}
        """).collect()

        res = [PrettyPrintDict(x) for x in df2.to_dicts()]
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
