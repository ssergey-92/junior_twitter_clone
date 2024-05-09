"""Start 'Fake Twitter' application."""
from signal import SIGINT, signal
from subprocess import run as subprocess_run
from typing import Optional
from types import FrameType


def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    """Catch signal 'SIGINT' keyboard interrupt.

    Stop and remove docker containers from docker compose

    Args:
        signum (int): signal number
        frame (Optional[FrameType]): object that represents the call stack at
        the time the signal is generated
    """
    subprocess_run(
        args="docker compose stop && docker compose rm",
        shell=True,
        input="y",
        encoding="utf-8",
    )


if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    start_fake_twitter = subprocess_run(
        args="docker compose -f docker-compose.yml up --build", shell=True,
    )
