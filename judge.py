import shutil
import subprocess
import tempfile
import itertools
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from collections import defaultdict
from typing import Iterable
import click

submission_root = Path('submissions')
testcase_root = Path('testcase')
verbose = 0


def get_score(code: Path) -> int:
    try:
        exe_path = compile(code)
    except subprocess.CalledProcessError:
        if verbose:
            print(f'Compile error {code}')
        return 0
    if verbose > 1:
        results = collect_results_sync(exe_path)
        print(f'Run submission {code}')
        for i, result in enumerate(results):
            print(f'Case #{i}: {"Pass" if result else "Fail"}')
    else:
        results = collect_results(exe_path)
        if verbose:
            results = [*results]
            print(f'Run submission {code}')
            for i, s in enumerate(results):
                print(f'Case #{i}: {"Pass" if s else "Fail"}')
    score = sum(10 for _ in filter(None, results))
    return score


def collect_results_sync(exe_path: Path) -> Iterable[bool]:
    results = []
    for i in range(10):
        testcase_pat = f'{i:02d}00'
        results.append(run_testcase(exe_path, testcase_pat))
    return results


def collect_results(exe_path: Path) -> Iterable[bool]:
    with ProcessPoolExecutor() as executor:
        patterns = []
        for i in range(10):
            testcase_pat = f'{i:02d}00'
            patterns.append(testcase_pat)
        results = executor.map(
            run_testcase,
            itertools.repeat(exe_path),
            patterns,
            timeout=30,
        )
    return results


def compile(code: Path) -> Path:
    tmp_file = tempfile.NamedTemporaryFile('wb', delete=False)
    subprocess.check_call(
        ['gcc', str(code), '-o', tmp_file.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return Path(tmp_file.name)


def run_testcase(exe_path: Path, testcase_pat: str) -> bool:
    student_exe_name = 'main'
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox = Path(sandbox)
        shutil.copy(testcase_root / (testcase_pat + '.log'), sandbox)
        shutil.copy(exe_path, sandbox / student_exe_name)
        try:
            subprocess.check_call(
                f'./{student_exe_name}',
                cwd=sandbox,
                timeout=3,
                stdin=(testcase_root / (testcase_pat + '.in')).open(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
        for ans_log in testcase_root.glob(f'{testcase_pat}.log-*'):
            student_log = sandbox / ans_log.name
            if not student_log.exists():
                return False
            if not cmp(ans_log.read_text(), student_log.read_text()):
                if verbose > 1:
                    output = Path('output')
                    (output / student_log.name).write_text(
                        student_log.read_text())
                return False
    return True


def cmp(a: str, b: str) -> bool:
    return preprocess_output(a) == preprocess_output(b)


def preprocess_output(s: str) -> str:
    s = s.splitlines()
    s = '\n'.join(l.rstrip() for l in s).rstrip()
    return s


@click.group()
@click.option('_verbose', '-v', '--verbose', count=True)
def main(_verbose: int):
    global verbose
    verbose = _verbose


@main.command()
@click.argument(
    'submission',
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=Path,
    ),
)
def judge_one(submission: Path):
    '''
    Judge single submission
    '''
    if verbose > 1:
        output = Path('output')
        if output.exists():
            shutil.rmtree(output)
        output.mkdir()
    score = get_score(submission)
    if verbose:
        print(f'Total score: {score}')
    else:
        print(score)


@main.command()
def judge_all():
    '''
    Judge all submissions
    '''
    scores = defaultdict(int)
    for user in submission_root.iterdir():
        print(f'Start {user}')
        with ProcessPoolExecutor() as executor:
            user_scores = executor.map(
                get_score,
                user.iterdir(),
                timeout=60,
            )
            scores[user.name] = max(user_scores)
    print(json.dumps(scores))


if __name__ == '__main__':
    main()
