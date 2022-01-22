import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.dev")
# Flag to differenciate web dyno from worker dyno
os.environ.setdefault('DYNO_TYPE', 'WORKER')
django.setup()

from django.conf import settings
from rq import Connection
from rq.worker import Worker as DefaultWorker, HerokuWorker

from pilot.queue.rq_setup import RQ_QUEUES
from pilot.utils.redis import redis_client

from multiprocessing import Pool, cpu_count

# Launch as much workers as the numbers of CPU core available, with a minimum count
MIN_WORKERS = 3
MAX_WORKERS = 16

if settings.ON_HEROKU:
    Worker = HerokuWorker
    # NEW 14/12/18 : One worker per cpu result in 8 workers on a  standard-1X dyno,
    # which consume too much memory (limited at 512 MB), because each process reload the whole codebase.
    # We limit to 4 worker max on heroku for now, to avoid exploding our memory limit.
    MAX_WORKERS = 4
elif os.name == 'nt':
    from rq_win import WindowsWorker
    Worker = WindowsWorker
else:
    Worker = DefaultWorker


if settings.SENTRY_WORKER_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.rq import RqIntegration
    from pilot.utils.sentry import SENTRY_RELEASE

    # No need to traces_sample_rate for the worker
    sentry_sdk.init(
        dsn=settings.SENTRY_WORKER_DSN,
        integrations=[RqIntegration()],
        release=SENTRY_RELEASE
    )


def start_worker():
    with Connection(redis_client):
        Worker(RQ_QUEUES).work()


if __name__ == '__main__':
    # Take the number of cpu, with a minimum
    worker_count = max(cpu_count(), MIN_WORKERS)
    # Limit the memory usage on heroku
    worker_count = min(worker_count, MAX_WORKERS)
    pool = Pool(processes=worker_count)

    try:
        for i in range(worker_count):
            pool.apply_async(start_worker)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
        exit()
