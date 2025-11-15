from http import HTTPStatus

from ninja import Router
from ninja.security import django_auth

from thisapp import utils
from thisapp.models import Board, Card, Membership
from thisapp.schemas import (CardCreateSchema, CardEditSchema, CardMoveSchema,
                             Message)

PATH = '/boards/{board_id}/cards'
router = Router(auth=django_auth, tags=['cards'])


@router.post(
    PATH,
    response={frozenset({HTTPStatus.CREATED, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message}
)
def create_card(request, board_id: int, payload: CardCreateSchema):
    """
    Creates a new card in a board.
    """
    board = Board.objects.filter(id=board_id).first()

    if not board:
        return HTTPStatus.NOT_FOUND, Message(details='The board not found.')

    if not Membership.objects.filter(board=board, user=request.user, is_owner=True).exists():
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner of the board can create cards.')

    board.cards.create(title=payload.title, content=payload.content)
    return HTTPStatus.CREATED, Message(details='The card created successfully')


@router.patch(
    PATH + '/{card_id}',
    response={frozenset({
        HTTPStatus.OK,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND}): Message}
)
def edit_card(request, board_id: int, card_id: int, payload: CardEditSchema):
    """
    Edits the title and content of a card.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    user_with_board = Membership.objects.filter(user=request.user, board_id=board_id).first()

    if not (user_with_board and user_with_board.is_owner):
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner can edit cards.')

    update_data = payload.model_dump(exclude_none=True)

    if not update_data:
        return HTTPStatus.BAD_REQUEST, Message(details='No fields to update.')

    for field, value in update_data.items():
        setattr(card, field, value)

    card.save()
    return HTTPStatus.OK, Message(details='The card edited successfully')


@router.patch(
    PATH + '/{card_id}/status',
    response={frozenset({
        HTTPStatus.OK,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
    }): Message}
)
def move_card(request, board_id: int, card_id: int, payload: CardMoveSchema):
    """
    Moves a card to a new status.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    user_with_board = Membership.objects.filter(user=request.user, board_id=board_id).first()

    if not user_with_board:
        return HTTPStatus.FORBIDDEN, Message(details='You are not a member of this board.')

    try:
        utils.move_card(card, payload.move_direction)
    except ValueError as e:
        return HTTPStatus.BAD_REQUEST, Message(details=str(e))

    return HTTPStatus.OK, Message(details='The card moved successfully')


@router.delete(
    PATH + '/{card_id}',
    response={
        HTTPStatus.NO_CONTENT: None,
        frozenset({HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message
    }
)
def delete_card(request, board_id: int, card_id: int):
    """
    Deletes a card from a board.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    if not Membership.objects.filter(board_id=board_id, user=request.user, is_owner=True).exists():
        return HTTPStatus.FORBIDDEN, Message(details='Only the owner of the board can delete cards.')

    card.delete()
    return HTTPStatus.NO_CONTENT, None
