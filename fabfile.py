import os
import platform
from fabric import task


DISCORD_SERVER_PYTHON_PATH = "main.py"
VENV_PATH = ".venv"


def _run_python(command, file):
    command.run(f"python {file}")


def _activate_env(command, venv_path, python_file):
    activate_env = os.path.join(
        venv_path, "Scripts" if os.name == "nt" else "bin", "activate"
    )
    command.run(
        f"source {activate_env} \
                && pip install -r requirements.txt \
                && python {python_file}"
    )


@task
def start_bot(command):
    # command.run("git pull")

    if os.getenv("VIRTUAL_ENV") is not None:
        print("Using virtualenv")
        print("Running bot...")
        _run_python(command, DISCORD_SERVER_PYTHON_PATH)
        return

    if os.path.exists(VENV_PATH):
        print("Virtualenv Found")
        print("Activating venv and running bot...")
        _activate_env(command, VENV_PATH, DISCORD_SERVER_PYTHON_PATH)
        return

    print("Virtualenv not found")
    print("Creating venv...")
    python_executable = "python" if platform.system() == "Windows" else "python3"
    command.run(f"{python_executable} -m venv .venv")

    print("Activating venv and running bot...")
    _activate_env(command, VENV_PATH, DISCORD_SERVER_PYTHON_PATH)
