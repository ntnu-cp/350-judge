import shutil
import subprocess
import tempfile
import json
import enum
from pathlib import Path
from collections import defaultdict
from typing import Generator
import click

submission_root = Path('submissions')
testcase_root = Path('testcase')
verbose = 0


class TestcaseResult(str, enum.Enum):
    AC = 'AC'
    WA_CONTENT = 'WA-CONTENT'
    WA_MISSING = 'WA-MISSING'
    RE = 'RE'
    TLE = 'TLE'


def get_score(code: Path) -> int:
    try:
        exe_path = compile(code)
    except subprocess.CalledProcessError:
        if verbose > 1:
            print(f'Compile error {code}')
        return 0
    if verbose:
        score = 0
        results = collect_results(exe_path)
        print(f'Run submission {code}')
        for i, s in enumerate(results):
            print(f'Case #{i}: {s}')
            if s == TestcaseResult.AC:
                score += 10
    else:
        results = collect_results(exe_path)
        score = sum(10 for r in results if r == TestcaseResult.AC)
    return score


def collect_results(exe_path: Path) -> Generator[TestcaseResult, None, None]:
    for i in range(10):
        testcase_pat = f'{i:02d}00'
        yield run_testcase(exe_path, testcase_pat)


def compile(code: Path) -> Path:
    tmp_file = tempfile.NamedTemporaryFile('wb', delete=False)
    subprocess.check_call(
        ['gcc', str(code), '-o', tmp_file.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return Path(tmp_file.name)


def run_testcase(exe_path: Path, testcase_pat: str) -> TestcaseResult:
    student_exe_name = 'main'
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox = Path(sandbox)
        shutil.copy(testcase_root / (testcase_pat + '.log'), sandbox)
        shutil.copy(exe_path, sandbox / student_exe_name)
        try:
            subprocess.check_call(
                f'./{student_exe_name}',
                cwd=sandbox,
                timeout=30,
                stdin=(testcase_root / (testcase_pat + '.in')).open(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return TestcaseResult.TLE
        except subprocess.CalledProcessError:
            return TestcaseResult.RE
        for ans_log in testcase_root.glob(f'{testcase_pat}.log-*'):
            student_log = sandbox / ans_log.name
            if not student_log.exists():
                return TestcaseResult.WA_MISSING
            if not cmp(ans_log.read_text(), student_log.read_text()):
                if verbose > 1:
                    output = Path('output')
                    (output / student_log.name).write_text(
                        student_log.read_text())
                return TestcaseResult.WA_CONTENT
    return TestcaseResult.AC


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
    if verbose > 1:
        output = Path('output')
        if output.exists():
            shutil.rmtree(output)
        output.mkdir()


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
        if verbose:
            print(f'Start {user}')
        scores[user.name] = max(get_score(d) for d in user.iterdir())
    print(json.dumps(scores))


if __name__ == '__main__':
    main()
