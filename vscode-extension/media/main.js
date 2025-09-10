// main.js - Cache panel script
(function () {
    const vscode = acquireVsCodeApi();
    
    const refreshButton = document.getElementById('refresh-button');
    const entriesContainer = document.getElementById('entries-container');
    
    // Handle refresh button click
    refreshButton.addEventListener('click', () => {
        vscode.postMessage({
            command: 'refresh'
        });
    });
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'updateEntries':
                renderEntries(message.entries);
                break;
            case 'error':
                showError(message.message);
                break;
        }
    });
    
    function renderEntries(entries) {
        if (entries.length === 0) {
            entriesContainer.innerHTML = '<div class="empty-state">No cache entries found</div>';
            return;
        }
        
        entriesContainer.innerHTML = entries.map(entry => `
            <div class="entry-item" data-cache-key="${entry.cacheKey}">
                <div class="entry-title">${escapeHtml(entry.prompt)}</div>
                <div class="entry-meta">
                    Created: ${new Date(entry.createdAt * 1000).toLocaleString()} | 
                    Accessed: ${entry.accessCount} times
                </div>
                ${entry.tags && entry.tags.length > 0 ? `
                    <div class="entry-tags">
                        ${entry.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        // Add click handlers for entries
        document.querySelectorAll('.entry-item').forEach(item => {
            item.addEventListener('click', () => {
                const cacheKey = item.getAttribute('data-cache-key');
                vscode.postMessage({
                    command: 'query',
                    cacheKey: cacheKey
                });
            });
        });
    }
    
    function showError(message) {
        entriesContainer.innerHTML = `<div class="empty-state">Error: ${escapeHtml(message)}</div>`;
    }
    
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}());