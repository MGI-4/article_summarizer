// Form validation utilities
const validateForm = {
    url: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    required: (value) => {
        return value && value.trim().length > 0;
    },
    
    maxLength: (value, max) => {
        return value.length <= max;
    }
};

// API utilities
const api = {
    async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    async get(url) {
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

// UI utilities
const ui = {
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="flex justify-center items-center">
                    <div class="loader"></div>
                    <span class="ml-2">Loading...</span>
                </div>
            `;
        }
    },
    
    hideLoading(elementId, content) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = content;
        }
    },
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative';
        errorDiv.role = 'alert';
        errorDiv.innerHTML = `
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline">${message}</span>
        `;
        
        document.body.insertBefore(errorDiv, document.body.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    },
    
    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative';
        successDiv.role = 'alert';
        successDiv.innerHTML = `
            <span class="block sm:inline">${message}</span>
        `;
        
        document.body.insertBefore(successDiv, document.body.firstChild);
        
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
};

// Date utilities
const dateUtils = {
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    getTimeframeDate(timeframe) {
        const date = new Date();
        switch (timeframe) {
            case 'daily':
                date.setDate(date.getDate() - 1);
                break;
            case 'weekly':
                date.setDate(date.getDate() - 7);
                break;
            case 'fortnightly':
                date.setDate(date.getDate() - 14);
                break;
            case 'monthly':
                date.setMonth(date.getMonth() - 1);
                break;
            case 'quarterly':
                date.setMonth(date.getMonth() - 3);
                break;
        }
        return date;
    }
};

// Export utilities for use in other files
window.appUtils = {
    validateForm,
    api,
    ui,
    dateUtils
};