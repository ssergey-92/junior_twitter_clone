from signal import SIGINT, signal
from subprocess import run as subprocess_run
from types import FrameType


def signal_handler(signum: int, frame: FrameType) -> None:
    subprocess_run(
        args="docker compose stop && docker compose rm",
        shell=True,
        input="y",
        encoding="utf-8",
    )


if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    start_fake_twitter = subprocess_run(
        args="docker compose -f docker-compose.yml up --build", shell=True
    )
