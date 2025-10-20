from .forms import CardForm
from .models import Card


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
