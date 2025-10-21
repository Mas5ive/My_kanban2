from collections import defaultdict

from .forms import CardForm
from .models import Board, Card


def split_boards(user_boards) -> dict[str, list[Board]]:
    """Splits a list of user's board memberships into two categories:
    boards where the user is an owner and boards where the user is a member (invited).

    Args:
        user_boards: A QuerySet of Membership objects, each representing a user's
                     relationship to a board.

    Returns:
        a dictionary with two keys: 'owner boards' and 'invitation boards'.
        Each key maps to a list of Board objects.
    """

    boards = defaultdict(list)
    for user in user_boards:
        if user.is_owner:
            boards['owner_boards'].append(user.board)
        else:
            boards['invitation_boards'].append(user.board)
    return boards


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
