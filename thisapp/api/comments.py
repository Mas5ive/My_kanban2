from http import HTTPStatus

from ninja import File, Form, Router
from ninja.files import UploadedFile
from ninja.security import django_auth

from thisapp.forms import CommentForm
from thisapp.models import Card, Membership
from thisapp.schemas import CommentSchema, CreateCommentSchema, Message

PATH = '/boards/{board_id}/cards/{card_id}/comments'
router = Router(auth=django_auth, tags=['comments'])


@router.get(
    PATH,
    response={
        HTTPStatus.OK: list[CommentSchema],
        frozenset({HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message
    }
)
def get_comments(request, board_id: int, card_id: int):  # Add parameters
    """
    Retrieves all comments for a specific card.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    if not Membership.objects.filter(user=request.user, board_id=board_id).exists():
        return HTTPStatus.FORBIDDEN, Message(details='You are not a member of this board.')

    comments = card.comments.select_related('author', 'card__board').all()
    return comments


@router.post(
    PATH,
    response={frozenset({
        HTTPStatus.CREATED,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
    }): Message}
)
def create_comment(
    request, board_id: int, card_id: int, data: Form[CreateCommentSchema], file: File[UploadedFile] = None
):
    """
    Creates a new comment on a card. Optionally, it is possible to attach a file to a comment.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    if not Membership.objects.filter(user=request.user, board_id=board_id).exists():
        return HTTPStatus.FORBIDDEN, Message(details='You are not a member of this board.')

    form = CommentForm(data.dict(), {'file': file} if file else None)

    if not form.is_valid():
        return HTTPStatus.BAD_REQUEST, Message(details=form.errors.as_text())

    comment = form.save(commit=False)
    comment.card = card
    comment.author = request.user
    comment.save()
    return HTTPStatus.CREATED, Message(details='The comment created successfully')


@router.delete(
    PATH + '/{comment_id}',
    response={
        HTTPStatus.NO_CONTENT: None,
        frozenset({HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}): Message
    }
)
def delete_comment(request, board_id: int, card_id: int, comment_id: int):
    """
    Deletes a comment from a card.
    """
    card = Card.objects.filter(id=card_id, board_id=board_id).first()

    if not card:
        return HTTPStatus.NOT_FOUND, Message(details='The card not found.')

    comment = card.comments.filter(id=comment_id).first()

    if not comment:
        return HTTPStatus.NOT_FOUND, Message(details='The comment not found.')

    user_with_board = Membership.objects.filter(user=request.user, board_id=board_id).first()

    if not user_with_board:
        return HTTPStatus.FORBIDDEN, Message(details='You are not a member of this board.')

    if not (user_with_board.is_owner or comment.author == request.user):
        return HTTPStatus.FORBIDDEN, Message(details='You can not delete this comment.')

    comment.delete()
    return HTTPStatus.NO_CONTENT, None
