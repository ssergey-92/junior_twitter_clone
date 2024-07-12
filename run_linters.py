"""Check application 'Junior Twitter Clone' by linters.

Install libraries for development from server/prod_requirements.txt than start
linter wemake-python-styleguide and mypy.
"""
from subprocess import run as subprocess_run


if __name__ == "__main__":
    subprocess_run(
        args="pip install -r server/dev_requirements.txt && "
        "echo ===================================================;"
        "echo Starting wemake-python-styleguide;"
        "flake8 main.py run_pytests.py run_linters.py Readme.md server/app;"
        "echo ===================================================;"
        "echo Starting mypy;"
        "cd server/app &&"
        "mypy --ignore-missing-imports --explicit-package-bases .;",
        shell=True,
        stdout=True,
        stderr=True,
        encoding="utf-8",
    )
