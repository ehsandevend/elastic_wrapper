import multiprocessing
import subprocess
from config.settings.integrations_config import GunicornConfig


def run_development():
    import uvicorn

    uvicorn.run(
        "config.routers:app",
        host=GunicornConfig.GUNICORN_HOST,
        port=GunicornConfig.GUNICORN_PORT,
        reload=True,
        log_level="debug",
        access_log=True,
        use_colors=True,
    )


def run_production():
    """Run gunicorn via subprocess (production mode)"""
    workers = multiprocessing.cpu_count() * 2 + 1

    gunicorn_command = [
        "gunicorn",
        "config.routers:app",
        "-k", "uvicorn.workers.UvicornWorker",
        "-w", f"{workers}",
        "-b", f"{GunicornConfig.GUNICORN_HOST}:{GunicornConfig.GUNICORN_PORT}",
        "--timeout", f"{GunicornConfig.GUNICORN_TIMEOUT}",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", GunicornConfig.GUNICORN_LOG_LEVEL,
    ]

    subprocess.run(gunicorn_command, check=True)


if __name__ == "__main__":
    if GunicornConfig.is_production():
        run_production()
    else:
        run_development()
