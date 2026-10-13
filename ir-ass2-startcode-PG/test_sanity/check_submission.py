"""Run the three mini workflow commands within three minutes."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

TIME_LIMIT_SECONDS = 180


def check_submission(config_name: str, api_key: str | None) -> None:
    """Pass your config to each stage without reading its structure."""
    deadline = time.monotonic() + TIME_LIMIT_SECONDS
    root = Path.cwd()
    config_file = root / config_name
    if not config_file.is_file():
        raise FileNotFoundError(f"Config not found: {config_file}")

    python = sys.executable
    api_key_args = ["--api_key", api_key] if api_key else []
    # Each stage reads your config and manages its own output paths.
    for stage in ("index.build", "rag_survey.retrieve", "rag_survey.judge"):
        _run([python, "-m", stage, "--config", config_name, *api_key_args], deadline)

    if time.monotonic() > deadline:
        raise TimeoutError("Mini workflow exceeded the three-minute limit")
    _print_status("[check] Mini workflow completed within three minutes.")
    _print_status("[check] Next, evaluate the newly generated mini CSV using its actual path.")
    _print_status("[check] Default path: python -m metrics.evaluate --submission runs/mini_best/submission.csv")
    _print_status("[check] If you changed the output location, replace this path with your new mini CSV path.")


def _run(command: list[str], deadline: float) -> None:
    """Run one stage within the shared time limit, hiding the key in progress text."""
    displayed = list(command)
    if "--api_key" in displayed:
        key_position = displayed.index("--api_key") + 1
        if key_position < len(displayed):
            displayed[key_position] = "YOUR_KEY"
    _print_status("[check] " + " ".join(displayed))
    stage = command[command.index("-m") + 1]
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Mini workflow exceeded the three-minute limit")
    try:
        subprocess.run(command, check=True, timeout=remaining)
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Mini workflow exceeded three minutes during {stage}") from None
    except subprocess.CalledProcessError as error:
        # CalledProcessError includes the command and its API key in its message.
        raise RuntimeError(
            f"{stage} failed with exit code {error.returncode}. See its error above."
        ) from None


def _print_status(message: str) -> None:
    """Keep command logging readable on Windows without importing project helpers."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    print(message.encode(encoding, errors="backslashreplace").decode(encoding), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="mini_config.ini")
    parser.add_argument("--api_key")
    arguments = parser.parse_args()
    check_submission(arguments.config, arguments.api_key)


if __name__ == "__main__":
    main()
