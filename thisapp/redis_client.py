import redis

from my_kanban2.settings import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

RECIPIENT_PREFIX = 'recipient:'
INVITATION_PREFIX = 'invitation:'

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
)
