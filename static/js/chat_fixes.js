// JavaScript for removing any remaining popup text and enhancing the chat button
document.addEventListener('DOMContentLoaded', function() {
    // Remove all existing popups
    const popups = document.querySelectorAll('.chat-popup, .popup-text, .chat-bubble');
    popups.forEach(popup => {
        popup.style.display = 'none';
        popup.remove(); // Completely remove the element
    });
    
    // Enhance the chat button
    const chatButton = document.querySelector('.chat-launcher');
    if (chatButton) {
        // Replace the button content with a simple icon (if it doesn't already exist)
        if (!chatButton.querySelector('.chat-icon')) {
            chatButton.innerHTML = `
                <span class="chat-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                </span>
            `;
        }
    }
});