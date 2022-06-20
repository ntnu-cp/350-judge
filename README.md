# judge script for CPII problem 350 - log query

## Links

- [Problem](https://v2.noj.tw/course/110-Computer-Programming-II/problem/350)
- Sample testcase is avaliable [here](https://idocntnu-my.sharepoint.com/:u:/g/personal/40747019s_eduad_ntnu_edu_tw/EW27VmA4_fBLi5SznEP59KgBXNmLON4kKtHyJv_JCQnRPA?e=MjTsYc).

## Cheatsheet

```bash
poetry run python judge.py -vv judge-one <your submission script>
# e.g. poetry run python judge.py -vv judge-one my-main.c
```

The output is like following:

```
Run submission my-main.c
Case #0: Pass
Case #1: Pass
Case #2: Pass
Case #3: Pass
Case #4: Pass
Case #5: Pass
Case #6: Pass
Case #7: Pass
Case #8: Pass
Case #9: Pass
Total score: 100
```

And you will see your program output in `output/` directory (if any):

```
output
├── 0000.log-2022-05-31
├── 0200.log-2022-09-01
├── 0300.log-2022-06-25
├── 0500.log-2022-09-13
├── 0600.log-2022-05-06
├── 0700.log-2023-04-13
└── 0800.log-2022-04-28
```

If you don't need to keep these log files, run this script with 1 or 0 `-v` option to decrease the verbose level.
e.g. `poetry run python judge.py judge-one my-main.c`

## Run Locally

### Requirements

- [Poetry](https://python-poetry.org/)

### Install dependency

```bash
poetry install
```

### Execute

```bash
poetry run python judge.py --help
```

## Run with Docker

### Requirements

- [Docker](https://python-poetry.org/)
- [Docker Compose](https://docs.docker.com/compose/)

### Build

```bash
docker-compose build
```

### Execute

```bash
docker-compose run --rm judger --help
```
