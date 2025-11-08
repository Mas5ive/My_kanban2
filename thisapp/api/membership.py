from http import HTTPStatus

from ninja import Router
from ninja.security import django_auth

import thisapp.invitations as invs
from thisapp.models import Board, Membership
from thisapp.schemas import (InvitationCreateSchema, InvitationPickSchema,
                             InvitationSchema, Message)
from user.models import CustomUser

router = Router(auth=django_auth, tags=['membership'])


@router.get('/invitations', response=list[InvitationSchema])
def get_invitations(request):
    """
    Returns a list of invitations for the requesting user.
    """
    user = request.user
    return invs.get_user_invitations(user.username)


@router.post(
    '/invitations',
    response={frozenset({
        HTTPStatus.CREATED,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
    }): Message}
)
def сreate_invitation(request, payload: InvitationCreateSchema):
    """
    Creates an invitation for a user to join a board.
    """
    sender = request.user
    board = Board.objects.filter(id=payload.board_id).first()

    if not board:
        return HTTPStatus.NOT_FOUND, Message(details='The board not found.')

    if not Membership.objects.filter(user=sender, board_id=payload.board_id, is_owner=True).exists():
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner of the board can send invitations.')

    recipient = CustomUser.objects.filter(username=payload.recipient).first()

    if not recipient:
        return HTTPStatus.NOT_FOUND, Message(details=f'The user “{payload.recipient}” not found.')

    if Membership.objects.filter(user=recipient, board_id=payload.board_id).exists():
        return (HTTPStatus.BAD_REQUEST,
                Message(details=f'The user “{payload.recipient}” is already a member of the board.'))

    if invs.get_invitation(payload.board_id, payload.recipient):
        return (HTTPStatus.BAD_REQUEST,
                Message(details=f'The user “{payload.recipient}” has already received an invitation.'))

    invs.create_invitation(payload.board_id, sender.username, recipient.username)
    return HTTPStatus.CREATED, Message(details='The invitation successfully sent!')


@router.post(
    '/boards/{board_id}/members',
    response={frozenset({HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND}): Message}
)
def create_member(request, board_id: int, payload: InvitationPickSchema):
    """
    Accepts or rejects a board invitation.
    """
    user = request.user

    if not invs.get_invitation(board_id, user.username):
        return HTTPStatus.NOT_FOUND, Message(details='The invitation not found.')

    if payload.operation == 'accept':
        Membership.objects.create(
            user=user,
            board_id=board_id
        )
        response = HTTPStatus.CREATED, Message(details='The invitation accepted.')
    elif payload.operation == 'reject':
        response = HTTPStatus.OK, Message(details='The invitation rejected.')

    invs.delete_invitation(board_id, user.username)
    return response


@router.delete(
    '/boards/{board_id}/members/{member}',
    response={
        HTTPStatus.NO_CONTENT: None,
        frozenset({HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message
    }
)
def delete_member(request, board_id: int, member: str):
    """
    Deletes a member from a board.
    """
    user = request.user
    board = Board.objects.filter(id=board_id).first()

    if not board:
        return HTTPStatus.NOT_FOUND, Message(details='The board not found.')

    if not Membership.objects.filter(user=user, board_id=board_id, is_owner=True).exists():
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner of the board can delete members.')

    member = CustomUser.objects.filter(username=member).first()

    if not member:
        return HTTPStatus.NOT_FOUND, Message(details='The member not found.')

    if not Membership.objects.filter(user=member, board_id=board_id, is_owner=False).exists():
        return (HTTPStatus.BAD_REQUEST,
                Message(details='incorrect operation for this user.'))

    Membership.objects.filter(user=member, board_id=board_id).delete()
    return HTTPStatus.NO_CONTENT, None
