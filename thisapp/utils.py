from collections import defaultdict
from typing import Literal

from .models import Card


def get_card_groups(board):
    """Groups cards by their status for a given board.

    Args:
        board: The Board object for which to group cards.

    Returns:
        A defaultdict where keys are Card.Status values and values are lists of
        Card objects belonging to that status.
    """
    grouped_cards = defaultdict(list)
    for card in board.cards.all():
        grouped_cards[card.status].append(card)
    return grouped_cards


def move_card(card: Card, move_direction: Literal['LEFT', 'RIGHT']) -> None:
    """
    Moves a card to the left or right in the workflow.

    Args:
        card: The Card object to move.
        move_direction: A string indicating the direction to move ('LEFT' or 'RIGHT').

    Raises:
        ValueError: If the move_direction is invalid for the card's current status.
    """
    match card.status, move_direction:
        case Card.Status.BACKLOG, 'RIGHT':
            card.status = Card.Status.IN_PROGRESS
        case Card.Status.IN_PROGRESS, 'LEFT':
            card.status = Card.Status.BACKLOG
        case Card.Status.IN_PROGRESS, 'RIGHT':
            card.status = Card.Status.DONE
        case Card.Status.DONE, 'LEFT':
            card.status = Card.Status.IN_PROGRESS
        case _:
            raise ValueError(f'Invalid operation: {move_direction} for the card status')

    card.save()
