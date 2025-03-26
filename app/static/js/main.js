// Function to update articles in the DOM
function updateArticles(articles) {
    const container = document.getElementById('articles-container');
    if (!container) return;
    
    if (!articles.length) {
        container.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-md text-center">
                <p class="text-gray-600">No articles found for your preferences.</p>
                <a href="/preferences" 
                   class="text-blue-500 hover:text-blue-600 inline-block mt-2">
                    Update your preferences
                </a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = articles.map(article => {
        // Process summary into bullet points
        let summaryHtml = '';
        if (article.summary) {
            const points = article.summary.split('\n')
                .filter(point => point.trim())
                .map(point => `<li class="text-gray-700">${point.trim().replace(/^[•-]\s*/, '')}</li>`)
                .join('');
            summaryHtml = `<ul class="list-disc list-inside space-y-2">${points}</ul>`;
        } else {
            summaryHtml = `<p class="text-gray-600 italic">Summary not available</p>`;
        }
        
        // Process sources used
        let sourcesHtml = '';
        if (article.sources_used && article.sources_used.length) {
            const sourcesList = article.sources_used.map(source => `
                <li>
                    <a href="${source.url}" target="_blank" 
                       class="text-blue-500 hover:text-blue-600 hover:underline">
                        ${source.title.length > 60 ? source.title.substring(0, 60) + '...' : source.title}
                    </a>
                </li>
            `).join('');
            
            sourcesHtml = `
                <div class="mt-4">
                    <h4 class="text-sm font-medium text-gray-700 mb-2">Citations:</h4>
                    <ul class="text-xs text-gray-600 space-y-1">
                        ${sourcesList}
                    </ul>
                </div>
            `;
        }
        
        return `
            <div class="article-card bg-white p-6 rounded-lg shadow-md transition-all duration-300">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-lg font-semibold text-gray-800">${article.title}</h3>
                    <span class="text-sm text-gray-500">${article.date}</span>
                </div>
                
                <div class="prose max-w-none mb-4">
                    ${summaryHtml}
                </div>
                
                <div class="border-t pt-4">
                    <div class="flex justify-between items-center text-sm">
                        <a href="${article.url}" 
                           target="_blank"
                           class="text-blue-500 hover:text-blue-600 flex items-center space-x-1">
                            <span>Read Original</span>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                        </a>
                        <span class="text-gray-500">Source: ${article.source}</span>
                    </div>
                    ${sourcesHtml}
                </div>
            </div>
        `;
    }).join('');
}

// Initialize the timeframe update handler
function initializeTimeframeHandler() {
    const timeframeSelect = document.getElementById('timeframe');
    if (timeframeSelect) {
        timeframeSelect.addEventListener('change', async () => {
            // Show loading state
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
            
            try {
                const formData = new FormData(document.getElementById('timeframeForm'));
                const response = await fetch('/update_timeframe', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    updateArticles(data.articles);
                } else {
                    throw new Error(data.error || 'Failed to update articles');
                }
            } catch (error) {
                console.error('Error updating timeframe:', error);
                alert('Error updating articles: ' + error.message);
            } finally {
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeTimeframeHandler();
});