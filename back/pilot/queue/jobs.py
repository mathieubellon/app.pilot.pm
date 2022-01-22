import threading
import uuid
import logging
from collections import namedtuple
try:
    import cPickle as pickle
except ImportError:  # noqa  # pragma: no cover
    import pickle

from multiprocessing.dummy import Process as DummyProcess
from multiprocessing.pool import ThreadPool

from django.db import connections
from django.db import transaction
from django.utils import timezone
from rq import get_current_job

from pilot.notifications.pilot_bot import get_pilot_bot_user
from pilot.queue.models import JobTracker
from pilot.queue.rq_setup import medium_priority_queue

logger = logging.getLogger(__name__)

# A thread-locale store for pending jobs
thread_local = threading.local()
thread_local.pending_jobs = []
# A data-structure that holds the data required to launch a job after the transaction
PendingJob = namedtuple('PendingJob', ['args', 'kwargs', 'job_id', 'job_class', 'depends_on', 'timeout'])


class SelfCleaningProcess(DummyProcess):
    """
    A thread that close db connections before shutdown.
    To be used as a Dummy Process into a multiprocessing.pool.ThreadPool
    """
    def run(self):
        super(SelfCleaningProcess, self).run()
        connections.close_all()


class SelfCleaningThreadPool(ThreadPool):
    """
    User threads that close their db connections
    """
    @staticmethod
    def Process(ctx, *args, **kwds):
        return SelfCleaningProcess(*args, **kwds)


class Job(object):
    """
    Launched Jobs are not enqueued immediately on the RQ queue.
    They are stored in a "pending jobs" list (which is thread-local).
    We wait for the database transaction to compelete sucesfully to actually enque them in RQ.
    This is generally when the web request/response cycle is done, because the ATOMIC_REQUESTS setting is True.
    """
    job_type = None
    queue = medium_priority_queue
    delete_tracker_on_success = False

    @staticmethod
    def reset_pending_jobs():
        """ Empty the pending jobs list """
        thread_local.pending_jobs = []

    @classmethod
    def enqueue_job(cls, args, kwargs, job_id, depends_on=None, timeout=None):
        try:
            cls.queue.enqueue_call(
                cls.start,
                args=args,
                kwargs=kwargs,
                job_id=job_id,
                depends_on=depends_on,
                timeout=timeout,
            )
        except:
            logger.error("[Job Enqueueing Error]\nJobTracker ID : {}".format(job_id), exc_info=True)
            job_tracker = JobTracker.objects.get(job_id=job_id)
            job_tracker.state = JobTracker.STATE_REDIS_DOWN
            job_tracker.save()

    @classmethod
    def add_pending_job(cls, args, kwargs, job_id, depends_on=None, timeout=None):
        """ Store a job to be enqueued after the db transaction """
        # The thread-locale is initialized in our PilotMiddleware.
        # But with the new django-channels architecture,
        # the middleware isn't always called,
        # and we may end up without an initialized thread-locale.
        # In this case, initialize it now.
        if not hasattr(thread_local, 'pending_jobs'):
            Job.reset_pending_jobs()

        thread_local.pending_jobs.append(
            PendingJob(
                args=args,
                kwargs=kwargs,
                job_id=job_id,
                job_class=cls,
                depends_on=depends_on,
                timeout=timeout
            )
        )

        # When we add the first pending job,
        # we must schedule a flush when the transaction commit
        if len(thread_local.pending_jobs) == 1:
            # If we're in a django thread, there will be a transaction around the view,
            # and we'll flush at the end of this transaction.
            # If we're in a job thread, there won't be any transaction, and the flush will occur immediatly,
            # the job will be launched right away
            transaction.on_commit(Job.flush_pending_jobs)

    @staticmethod
    def flush_pending_jobs():
        """ When the db transaction is over, we can safely enqueue the pending jobs """
        for pending_job in thread_local.pending_jobs:
            pending_job.job_class.enqueue_job(
                args=pending_job.args,
                kwargs=pending_job.kwargs,
                job_id=pending_job.job_id,
                depends_on=pending_job.depends_on,
                timeout=pending_job.timeout
            )

        # Reset the pending jobs after a flush
        Job.reset_pending_jobs()

    @classmethod
    def launch(cls, desk, user=None, *args, **kwargs):
        """ The job may be launched either from a django request/response thread,
        or from another job.

        If we're in a django thread, we prepare the job to be enqueued by adding it into the pending jobs list.
        If we're in a job thread, then we can enqueue the job right away.
        """
        # Create ourselve the job id, so we can create the JobTracker first.
        # This is to ensure that we can retrieve the JobTracker (by its job_id) when the job start
        job_id = str(uuid.uuid4())

        # If no user has been provided, we use the user bot to ensure created_by as something inside it
        if not user:
            user = get_pilot_bot_user()

        depends_on = kwargs.pop('depends_on', None)
        timeout = kwargs.pop('timeout', None)

        job_tracker = JobTracker.objects.create(
            desk=desk,
            created_by=user,
            job_id=job_id,
            job_type=cls.job_type,
            args=args,
            kwargs=kwargs,
            timeout=timeout
        )

        cls.add_pending_job(args, kwargs, job_id, depends_on, timeout)

        return {
            'job_id': job_id,
            'job_tracker': job_tracker
        }

    @classmethod
    def launch_r(cls, request, *args, **kwargs):
        return cls.launch(request.desk, request.user, *args, **kwargs)

    @classmethod
    def launch_sync(cls, desk, user, *args, **kwargs):
        job_tracker = JobTracker(desk=desk, created_by=user)
        job = cls(None, job_tracker)
        return job.run(*args, **kwargs)

    @classmethod
    def start(cls, *args, **kwargs):
        logger.info(f"Starting Job {cls.__name__} with ({args}), {{{kwargs}}}")
        rq_job = get_current_job()

        try:
            job_tracker = JobTracker.objects.get(job_id=rq_job.id)
        except:
            logger.error("[Job Error]\nRQ job ID : {}".format(rq_job.id), exc_info=True)
            # re-raise, so RQ can move the job to the failed queue
            raise

        try:
            job_tracker.state = JobTracker.STATE_STARTED
            job_tracker.save()
            # Run the job inside a transaction,
            # so the db does not end up in an intermediate state in case of error
            with transaction.atomic():
                job = cls(rq_job, job_tracker)
                result = job.run(*args, **kwargs)
        except:
            logger.error("[Job Error]\nRQ job ID : {}\nJobTracker ID : {}".format(rq_job.id, job_tracker.id), exc_info=True)
            job_tracker.state = JobTracker.STATE_FAILED
            job_tracker.save()
            # re-raise, so RQ can move the job to the failed queue
            raise

        if cls.delete_tracker_on_success:
            job_tracker.delete()
        else:
            job_tracker.finished_at = timezone.now()
            job_tracker.state = JobTracker.STATE_FINISHED
            job_tracker.save()

        return result

    def __init__(self, rq_job, job_tracker):
        self.rq_job = rq_job
        self.job_tracker = job_tracker

    def run(self, *args, **kwargs):
        raise NotImplementedError()
