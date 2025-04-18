// JavaScript for removing any "how can I help" popup text
document.addEventListener('DOMContentLoaded', function() {
    // Remove all popup elements while keeping the chat button
    const popups = document.querySelectorAll('.chat-popup, .popup-text, .chat-bubble, .how-can-i-help, .chatbot-popup');
    popups.forEach(popup => {
        popup.style.display = 'none';
        popup.remove(); // Completely remove the element
    });
});