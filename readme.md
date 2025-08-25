

## Скрипт для парсинга логов.


## Возможные параметры:

--report_size размер отчёта (в строках)

--report_dir директория, куда класть отчёт

--log_dir директория с логами


## Пример сборки и запуска:

```console
foo@bar:~$ docker build --no-cache --squash -t python_hw_1 -f docker/Dockerfile .
foo@bar:~$ docker run -v ~/PycharmProjects/python_2025_1:/src -it python_hw_1 /bin/bash
foo@bar:~$ uv run python_2025_1/log_analyzer.py
```
