import subprocess
import sys


def run_frontend_main():
    subprocess.run([sys.executable, "-m", "frontend.main"])


if __name__ == "__main__":
    run_frontend_main()
