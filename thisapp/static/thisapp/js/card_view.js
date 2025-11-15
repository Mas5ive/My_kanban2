import { deleteCard, editCard } from './apiService.js';

document.addEventListener('DOMContentLoaded', () => {

    // Event listener for deleting a card
    const deleteCardForm = document.getElementById('delete-card-form');
    if (deleteCardForm) {
        deleteCardForm.addEventListener('submit', async (event) => {

            if (!confirm('Are you sure you want to delete this card?')) {
                return;
            }

            event.preventDefault();
            const form = event.target;
            const boardId = form.dataset.boardId;
            const cardId = form.dataset.cardId;
            await deleteCard(boardId, cardId);
            window.location.href = `/boards/${boardId}`;
        });
    }

    // Event listener for editing a card
    const editCardForm = document.getElementById('edit-card-form');
    if (editCardForm) {
        editCardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const boardId = form.dataset.boardId;
            const cardId = form.dataset.cardId;
            const title = form.elements.title.value;
            const content = form.elements.content.value;
            const result = await editCard(boardId, cardId, title, content);
            alert(result.details || 'An unknown error occurred.');
        });
    }
});