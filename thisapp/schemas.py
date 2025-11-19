from typing import Literal

from ninja import ModelSchema, Schema
from pydantic import Field

from .models import Board, Comment


class BoardSchema(ModelSchema):
    class Meta:
        model = Board
        exclude = ['members']


class BoardCreateSchema(Schema):
    title: str = Field(
        ...,
        min_length=1,
        max_length=Board._meta.get_field('title').max_length,
        pattern=r'.*\S.*'
    )


class UserBoardsSchema(Schema):
    owner_boards: list[BoardSchema]
    member_boards: list[BoardSchema]


class InvitationSchema(Schema):
    sender_name: str
    board_id: int
    board_title: str


class InvitationCreateSchema(Schema):
    board_id: int
    recipient: str


class InvitationPickSchema(Schema):
    operation: Literal['accept', 'reject']


class CardSchema(Schema):
    content: str | None = None


class CardCreateSchema(CardSchema):
    title: str = Field(..., min_length=1, pattern=r'.*\S.*')


class CardEditSchema(CardSchema):
    title: str = Field(None, min_length=1, pattern=r'.*\S.*')


class CardMoveSchema(Schema):
    move_direction: Literal['LEFT', 'RIGHT']


class CommentSchema(ModelSchema):
    filename: str | None = None
    file_url: str | None = None
    author_username: str = Field(..., alias='author.username')

    class Meta:
        model = Comment
        exclude = ['card', 'author', 'file']

    @staticmethod
    def resolve_filename(obj: Comment) -> str | None:
        return obj.get_filename()

    @staticmethod
    def resolve_file_url(obj: Comment) -> str | None:
        return obj.get_file_url()


class CreateCommentSchema(Schema):
    content: str = Field(..., min_length=1, pattern=r'.*\S.*')


class Message(Schema):
    details: str
