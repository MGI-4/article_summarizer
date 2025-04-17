/**
 * Main JavaScript file for the Article Summarizer application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any global elements
    initializeFlashMessages();
});

/**
 * Initialize flash messages to auto-dismiss after a delay
 */
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('[role="alert"]');
    
    flashMessages.forEach(message => {
        // Add close button to each flash message
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'ml-4 text-lg font-bold';
        closeButton.addEventListener('click', () => {
            message.remove();
        });
        
        // Add close button to the message
        message.querySelector('p').appendChild(closeButton);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            
            // Remove from DOM after fade out
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
}

/**
 * Format a date string as MM/DD/YYYY
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const year = date.getFullYear();
    
    return `${month}/${day}/${year}`;
}

/**
 * Validate an email address format
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid, false otherwise
 */
function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait between calls
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Toggle element visibility
 * @param {HTMLElement} element - Element to toggle
 */
function toggleVisibility(element) {
    if (element.classList.contains('hidden')) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

/**
 * Create an element with attributes and content
 * @param {string} tag - HTML tag name
 * @param {object} attributes - Attributes to set on the element
 * @param {string|HTMLElement} content - Content to append to the element
 * @returns {HTMLElement} The created element
 */
function createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    // Set attributes
    for (const [key, value] of Object.entries(attributes)) {
        element.setAttribute(key, value);
    }
    
    // Set content
    if (typeof content === 'string') {
        element.textContent = content;
    } else if (content instanceof HTMLElement) {
        element.appendChild(content);
    }
    
    return element;
}