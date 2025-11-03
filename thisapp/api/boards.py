from http import HTTPStatus

from django.db import transaction
from ninja import Router
from ninja.security import django_auth

import thisapp.invitations as invs
from thisapp.models import Board, Membership
from thisapp.schemas import BoardCreateSchema, Message, UserBoardsSchema

PATH = '/boards'
router = Router(auth=django_auth, tags=['boards'])


@router.get(PATH, response=UserBoardsSchema)
def get_boards(request):
    """Returns a list of boards that the user owns and is a member of, along with any pending invitations."""
    user_boards = Membership.objects.filter(user=request.user).select_related('board')
    owner_boards = [membership.board for membership in user_boards if membership.is_owner]
    member_boards = [membership.board for membership in user_boards if not membership.is_owner]
    return UserBoardsSchema(owner_boards=owner_boards, member_boards=member_boards)


@router.post(PATH, response={HTTPStatus.CREATED: Message})
def create_board(request, payload: BoardCreateSchema):
    """
    Creates a new board with the requesting user as the owner.
    """
    with transaction.atomic():
        board = Board.objects.create(title=payload.title)
        Membership.objects.create(
            user=request.user,
            board=board,
            is_owner=True
        )
    return HTTPStatus.CREATED, Message(details='The board created successfully')


@router.delete(
    PATH + '/{board_id}',
    response={
        HTTPStatus.NO_CONTENT: None,
        frozenset({HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message
    }
)
def delete_board(request, board_id: int):
    """
    Deletes a board and all associated invitations.
    """
    board = Board.objects.filter(id=board_id).first()

    if not board:
        return HTTPStatus.NOT_FOUND, Message(details='The board not found.')

    user = request.user
    user_with_board = Membership.objects.filter(user=user, board_id=board_id).first()

    if not (user_with_board and user_with_board.is_owner):
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner can delete boards.')

    board.delete()
    invs.delete_board_invitations(board_id)
    return HTTPStatus.NO_CONTENT, None
