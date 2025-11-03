import { getBoards, createBoard } from './apiService.js';

function createBoardElement(board) {
    const form = document.createElement('form');
    form.action = `/boards/${board.id}`;
    form.method = 'get';

    const button = document.createElement('button');
    button.className = 'board-button';
    button.textContent = board.title;

    form.appendChild(button);
    return form;
}


function renderBoards(boardsData) {
    ['owner', 'member'].forEach(key => {
        const container = document.getElementById(`${key}-boards-container`);
        const section = document.getElementById(`${key}-boards-section`);

        if (!container || !section) return;

        container.innerHTML = '';
        section.style.display = 'none';

        if (boardsData[`${key}_boards`].length > 0) {
            section.style.display = 'block';
            boardsData[`${key}_boards`].forEach(board => container.appendChild(createBoardElement(board)));
        }
    });
}


document.addEventListener('DOMContentLoaded', async () => {
    const boardsData = await getBoards();
    renderBoards(boardsData);

    // Event listener for creating a new board
    document.getElementById('create-board-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const title = form.elements.title.value;
        await createBoard(title);
        const updatedBoards = await getBoards();
        renderBoards(updatedBoards);
        form.reset();
    });
});
