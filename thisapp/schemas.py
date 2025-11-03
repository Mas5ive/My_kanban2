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


class Message(Schema):
    details: str
