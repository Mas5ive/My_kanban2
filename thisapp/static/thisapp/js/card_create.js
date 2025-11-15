import { createCard } from './apiService.js';

document.addEventListener('DOMContentLoaded', () => {

    // Event listener for creating a new card
    const createCardForm = document.getElementById('create-card-form');
    if (createCardForm) {
        createCardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const boardId = form.dataset.boardId;
            const title = form.elements.title.value;
            const content = form.elements.content.value;
            await createCard(boardId, title, content);
            window.location.href = `/boards/${boardId}`;
        });
    }
});