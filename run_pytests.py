"""Start pytest for project 'Junior Twitter Clone'."""
from subprocess import Popen as subprocess_Popen
from subprocess import run as subprocess_run
from time import sleep

if __name__ == "__main__":
    docker_compose_for_test_db = subprocess_Popen(
        args="docker compose -f server/tests/docker-compose.yml up --build",
        shell=True,
    )
    sleep(2)  # time to create the container with test_db
    subprocess_run(
        args="timeout 15s docker exec test_postgresql sh -c 'pg_isready' && "
        "pytest --cov-report term-missing --cov=server/app server/tests -v ;"
        "cd server/tests && "
        "docker compose stop && "
        "docker compose rm",
        shell=True,
        stdout=True,
        stderr=True,
        input="y",
        encoding="utf-8",
    )
