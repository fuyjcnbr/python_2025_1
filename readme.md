


main prints "lala"


docker build --no-cache --squash -t python_hw_1 -f Dockerfile .


docker run -it python_hw_1 /bin/bash

docker run -v ~/PycharmProjects/python_2025_1:/src -it python_hw_1 /bin/bash



make -B tests

make tests

uv lock
