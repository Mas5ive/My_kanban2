import { deleteBoard, deleteMember, createInvitation } from './apiService.js';


document.addEventListener('DOMContentLoaded', () => {

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