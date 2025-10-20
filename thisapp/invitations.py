import json

from .models import Board
from .redis_client import redis_client

RECIPIENT_PREFIX = 'recipient:'
INVITATION_PREFIX = 'invitation:'


def get_invitation(board_id: int, recipient: str) -> bytes | None:
    invitation_key = INVITATION_PREFIX + recipient + f':{board_id}'
    return redis_client.get(invitation_key)


def create_invitation(board_id: int, sender: str, recipient: str, ttl=60) -> None:
    invitation_key = INVITATION_PREFIX + recipient + f':{board_id}'
    recipient_key = RECIPIENT_PREFIX + recipient

    board = Board.objects.get(id=board_id)

    invitation_value = {
        'sender_name': sender,
        'board_id': board.id,
        'board_title': board.title
    }
    redis_client.set(invitation_key, json.dumps(invitation_value), ex=ttl)
    redis_client.sadd(recipient_key, invitation_key)
    redis_client.expire(recipient_key, time=ttl)


def delete_invitation(board_id: int, recipient: str) -> None:
    invitation_key = INVITATION_PREFIX + recipient + f':{board_id}'
    recipient_key = RECIPIENT_PREFIX + recipient
    redis_client.delete(invitation_key)
    redis_client.srem(recipient_key, invitation_key)


def get_user_invitations(recipient: str) -> list[str]:
    recipient_key = RECIPIENT_PREFIX + recipient
    invitation_keys = redis_client.smembers(recipient_key)
    return [json.loads(invitation) for key in invitation_keys if (invitation := redis_client.get(key))]


def delete_board_invitations(board_id: int) -> None:
    cursor = 0

    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=INVITATION_PREFIX + '*' + f':{board_id}')
        if keys:
            redis_client.delete(*keys)
            for invitation_key in keys:
                key_str = invitation_key.decode()
                recipient = key_str.split(':')[1]
                recipient_key = RECIPIENT_PREFIX + recipient
                redis_client.srem(recipient_key, invitation_key)
        if cursor == 0:
            break
