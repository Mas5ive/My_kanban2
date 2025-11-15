import { deleteBoard, deleteMember, createInvitation, moveCard } from './apiService.js';


function updateMoveButtons(cardElement) {
    const column = cardElement.closest('.column');

    if (!column) return;

    const moveLeftButton = cardElement.querySelector('.move-card-button[data-move-direction="LEFT"]');
    const moveRightButton = cardElement.querySelector('.move-card-button[data-move-direction="RIGHT"]');

    if (moveLeftButton) {
        moveLeftButton.style.display = column.previousElementSibling?.classList.contains('column') ? 'block' : 'none';
    }

    if (moveRightButton) {
        moveRightButton.style.display = column.nextElementSibling?.classList.contains('column') ? 'block' : 'none';
    }
}

function updateColumnCounter(column) {
    const counter = column.querySelector('h2');
    const cardCount = column.querySelectorAll('.card').length;

    if (counter) {
        counter.textContent = counter.textContent.replace(/\[\d*\]/, `[${cardCount}]`);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card').forEach(updateMoveButtons);

    // Event listener for moving cards
    const board = document.querySelector('.board');
    if (board) {
        board.addEventListener('click', async (event) => {
            const button = event.target.closest('.move-card-button');

            if (!button) return;

            event.preventDefault();
            const { boardId, cardId, moveDirection } = button.dataset;
            await moveCard(boardId, cardId, moveDirection);
            const cardElement = button.closest('.card');
            const currentColumn = cardElement.closest('.column');
            const columns = Array.from(board.querySelectorAll('.column'));
            const currentColumnIndex = columns.indexOf(currentColumn);

            let targetColumn;

            if (moveDirection === 'RIGHT') {
                targetColumn = columns[currentColumnIndex + 1];
            } else if (moveDirection === 'LEFT') {
                targetColumn = columns[currentColumnIndex - 1];
            }

            if (targetColumn && cardElement) {
                targetColumn.querySelector('.scrollable').appendChild(cardElement);
                updateMoveButtons(cardElement);
                updateColumnCounter(currentColumn);
                updateColumnCounter(targetColumn);
            }
        });
    }

    // Event listener for deleting members  
    const membersContainer = document.querySelector('.members .scrollable');
    if (membersContainer) {
        membersContainer.addEventListener('click', async (event) => {

            if (!event.target.classList.contains('delete-member-button')) {
                return;
            }

            event.preventDefault();
            const button = event.target;
            const boardId = button.dataset.boardId;
            const username = button.dataset.username;

            if (!confirm(`Are you sure you want to remove ${username} from this board?`)) {
                return;
            }

            await deleteMember(boardId, username);
            button.closest('.member').remove();
        });
    }

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

    // Event listener for inviting members
    const inviteForm = document.getElementById('invite-form');
    if (inviteForm) {
        inviteForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const boardId = form.dataset.boardId;
            const recipient = form.elements.recipient.value;
            const result = await createInvitation(boardId, recipient);
            form.reset();
            alert(result.details);
        });
    }
});