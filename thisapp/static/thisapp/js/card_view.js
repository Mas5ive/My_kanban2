import { createComment, deleteCard, editCard, getComments, deleteComment } from './apiService.js';
import { formatDate } from './utils.js';


function createCommentElement(comment, boardId, cardId, currentUsername, isUserBoardOwner) {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment';
    commentDiv.dataset.commentId = comment.id;
    const formattedDate = formatDate(comment.date);

    const authorP = document.createElement('p');
    authorP.textContent = `${comment.author_username} (${formattedDate})`;

    const contentP = document.createElement('p');
    contentP.textContent = comment.content;
    contentP.style.whiteSpace = 'pre-wrap';

    commentDiv.appendChild(authorP);
    commentDiv.appendChild(contentP);

    if (comment.filename && comment.file_url) {
        const contentFileLink = document.createElement('p');
        const fileLink = document.createElement('a');
        fileLink.href = comment.file_url;
        fileLink.textContent = comment.filename;
        fileLink.download = comment.filename;
        contentFileLink.appendChild(fileLink);
        commentDiv.appendChild(contentFileLink);
    }

    if (isUserBoardOwner || comment.author_username === currentUsername) {
        const deleteForm = document.createElement('form');
        deleteForm.className = 'delete-comment-form';
        deleteForm.dataset.boardId = boardId;
        deleteForm.dataset.cardId = cardId;
        deleteForm.dataset.commentId = comment.id;
        deleteForm.innerHTML = `
            <button class="delete-comment-button">Delete</button>
            <div style="clear: both;"></div>
        `;
        commentDiv.appendChild(deleteForm);
    }

    return commentDiv;
}

function renderComments(commentsContainer, comments, boardId, cardId, currentUsername, isUserBoardOwner) {
    commentsContainer.innerHTML = ''
    comments.forEach(comment => {
        const commentElement = createCommentElement(comment, boardId, cardId, currentUsername, isUserBoardOwner);
        commentsContainer.appendChild(commentElement);
    });
}


document.addEventListener('DOMContentLoaded', async () => {
    const commentsSection = document.querySelector('.comments');

    if (!commentsSection) return;

    const commentsContainer = document.querySelector('.comments .scrollable');
    let { boardId, cardId, currentUsername, isUserBoardOwner } = commentsContainer.dataset;
    isUserBoardOwner = Boolean(Number(isUserBoardOwner));
    const comments = await getComments(boardId, cardId);
    renderComments(commentsContainer, comments, boardId, cardId, currentUsername, isUserBoardOwner);

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

    // Event listener for creating a new comment
    const createCommentForm = document.getElementById('create-comment-form');
    if (createCommentForm) {
        createCommentForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = event.target;
            const result = await createComment(boardId, cardId, form);
            form.reset();
            alert(result.details || 'An unknown error occurred.');
            const comments = await getComments(boardId, cardId);
            renderComments(commentsContainer, comments, boardId, cardId, currentUsername);
        });
    }

    // Event listener for deleting a comment
    if (commentsContainer) {
        commentsContainer.addEventListener('submit', async (event) => {

            if (!event.target.classList.contains('delete-comment-form')) return;

            event.preventDefault();
            const form = event.target;
            const { boardId, cardId, commentId } = form.dataset;
            await deleteComment(boardId, cardId, commentId);
            form.closest('.comment').remove();
        });
    }
});
