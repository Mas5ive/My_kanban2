/**
 * Formats a date string into a localized, human-readable format.
 * Example: "2023-10-27 10:30"
 * @param {string|Date} dateInput - The date string or Date object to format.
 * @returns {string} The formatted date string.
 */
export function formatDate(dateInput) {
    try {
        const date = new Date(dateInput);
        // Using 'sv-SE' locale for consistent YYYY-MM-DD HH:MM format
        return date.toLocaleString('sv-SE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error("Error formatting date:", dateInput, error);
        return String(dateInput); // Return original input if formatting fails
    }
}