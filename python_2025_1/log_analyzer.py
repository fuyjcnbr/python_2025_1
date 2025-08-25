# import glob
# from typing import Optional, Any

# from dataclasses import dataclass
# from enum import Enum
from pathlib import Path
# import gzip
import sys
import argparse
import logging
# import polars as pl
# import pandas as pd


sys.path.insert(1, str(Path(__file__).parent.parent.resolve()))
from python_2025_1.misc.worker import Worker

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "report_size": 100,
    "report_dir": "report",
    "log_dir": "data"
}


parser = argparse.ArgumentParser()
parser.add_argument("--report_size", type=str, required=False, default=config["report_size"])
parser.add_argument("--report_dir", type=str, required=False, default=config["report_dir"])
parser.add_argument("--log_dir", type=str, required=False, default=config["log_dir"])
args = parser.parse_args()


def main():
    # files = [f for f in os.listdir('./data') if Worker.is_log(f) != FileType.Unknown]
    # glob.glob('145592*.jpg')
    # nginx - access - ui.log - YYYYMMDD.gz
    # print(os.listdir('../data'))
    logger = logging.getLogger(__name__)

    logger_kwargs = dict(
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s;%(name)s;%(levelname)s;%(message)s",
    )
    # logger_kwargs["filename"] = "log_analyzer.log"
    logger_kwargs["stream"] = sys.stdout
    logging.basicConfig(**logger_kwargs)

    # logging.basicConfig(
    #     filename="log_analyzer.log",
    #     encoding="utf-8",
    #     level=logging.INFO,
    #     format="%(asctime)s;%(name)s;%(levelname)s;%(message)s",
    # )
    # logging.basicConfig(
    #     stream=sys.stdout,
    #     encoding="utf-8",
    #     level=logging.INFO,
    #     format="%(asctime)s;%(name)s;%(levelname)s;%(message)s",
    # )
    # handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    logger.info("starting")
    w = Worker(log_dir="data", report_dir="report", logger=logger)
    log = w.get_log()
    # print(log)
    li = w.get_log_stats(log)
    w.generate_report(log, li)
    logger.info("finished")


if __name__ == "__main__":
    main()
