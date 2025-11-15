from typing import Literal

from ninja import ModelSchema, Schema
from pydantic import Field

from .models import Board


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


class Message(Schema):
    details: str
