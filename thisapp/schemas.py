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


class Message(Schema):
    details: str
