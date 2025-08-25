
from python_2025_1.misc.misc import FileType
from python_2025_1.misc.worker import Worker


def test_log_type_gz():
    file_type = Worker.log_type("nginx-access-ui.log-20170630.gz")
    assert(file_type == FileType.Gz)

def test_log_type_text():
    file_type = Worker.log_type("nginx-access-ui.log-20170630")
    assert(file_type == FileType.Text)

def test_log_type_unknown():
    file_type = Worker.log_type("access-ui.log-20170630")
    assert(file_type == FileType.Unknown)
