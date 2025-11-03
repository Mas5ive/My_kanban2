// Base URL for API requests
const API_BASE_URL = '/api/v1';

class APIError extends Error {
    constructor(message) {
        super(message);
        this.name = 'APIError';
    }
}

async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const method = options.method ? options.method.toUpperCase() : 'GET';

    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
        options.headers = { ...options.headers,
            'X-CSRFToken': csrfToken,
        };
    }
    const response = await fetch(url, { ...options, headers: options.headers });

    if (!response.ok) {
        let details = `HTTP error! status: ${response.status}`;
        try {
            const errorData = await response.json();
            details = errorData.details || details;
        } catch (e) {
            console.error("Could not parse error response as JSON", e);
        }
        alert(details);
        throw new APIError(details);
    }

    return response.json();
}


// --- Board related API calls ---

export async function getBoards() {
    return apiFetch('/boards');
}

export async function createBoard(title) {
    return apiFetch('/boards', {
         method: 'POST' ,
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ title }),
    });
}

export async function deleteBoard(boardId) {
    return apiFetch(`/boards/${boardId}`, { method: 'DELETE' });
}

