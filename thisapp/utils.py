import json

from redis_db import INVITATION_PREFIX, RECIPIENT_PREFIX, redis_client

from .forms import CardForm
from .models import Board, Card


def move_card(card: Card, operation: str):
    match card.status, operation:
        case Card.Status.BACKLOG, 'MOVE_RIGHT':
            card.status = Card.Status.IN_PROGRESS
        case Card.Status.IN_PROGRESS, 'MOVE_LEFT':
            card.status = Card.Status.BACKLOG
        case Card.Status.IN_PROGRESS, 'MOVE_RIGHT':
            card.status = Card.Status.DONE
        case Card.Status.DONE, 'MOVE_LEFT':
            card.status = Card.Status.IN_PROGRESS
        case _:
            return False
    card.save()
    return True


def edit_card(form: CardForm, card: Card):
    if not form.is_valid():
        return False, form.errors

    changed_card = form.save(commit=False)
    card.title = changed_card.title
    card.content = changed_card.content
    card.save()
    return True, form.errors


def delete_card(card: Card):
    card.delete()
    return True


def get_invitation(board_id: int, recipient: str):
    invitation_key = INVITATION_PREFIX + recipient + f':{board_id}'
    return redis_client.get(invitation_key)


def create_invitation(board_id: int, sender: str, recipient: str, ttl=60):
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


def delete_invitation(board_id: int, recipient: str):
    invitation_key = INVITATION_PREFIX + recipient + f':{board_id}'
    recipient_key = RECIPIENT_PREFIX + recipient
    redis_client.delete(invitation_key)
    redis_client.srem(recipient_key, invitation_key)


def get_user_invitations(recipient: str):
    recipient_key = RECIPIENT_PREFIX + recipient
    invitation_keys = redis_client.smembers(recipient_key)
    return [json.loads(invitation) for key in invitation_keys if (invitation := redis_client.get(key))]


def delete_board_invitations(board_id: int):
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
