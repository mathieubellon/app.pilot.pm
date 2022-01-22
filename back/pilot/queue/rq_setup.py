from rq import Queue

from pilot.utils.redis import redis_client

HIGH_PRIORITY = 'high'
MEDIUM_PRIORITY = 'medium'
LOW_PRIORITY = 'low'
RQ_QUEUES = [HIGH_PRIORITY, MEDIUM_PRIORITY, LOW_PRIORITY]

high_priority_queue = Queue(name=HIGH_PRIORITY, connection=redis_client)
medium_priority_queue = Queue(name=MEDIUM_PRIORITY, connection=redis_client)
low_priority_queue = Queue(LOW_PRIORITY, connection=redis_client)