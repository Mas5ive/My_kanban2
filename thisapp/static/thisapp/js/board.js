import { deleteBoard } from './apiService.js';


document.addEventListener('DOMContentLoaded', () => {

    // Event listener for deleting board
    const deleteBoardButton = document.getElementById('delete-board-button');
    if (deleteBoardButton) {
        deleteBoardButton.addEventListener('click', async (event) => {

            if (!confirm('Are you sure you want to delete this board? This action cannot be undone.')) {
                return;
            }

            event.preventDefault();
            const button = event.target;
            const boardId = button.dataset.boardId;
            await deleteBoard(boardId);
            window.location.href = '/profile';
        });
    }
});