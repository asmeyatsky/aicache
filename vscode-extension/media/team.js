// team.js - Team presence script
(function () {
    const vscode = acquireVsCodeApi();
    
    const refreshButton = document.getElementById('refresh-button');
    const membersContainer = document.getElementById('members-container');
    
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
            case 'updateMembers':
                renderMembers(message.members);
                break;
            case 'error':
                showError(message.message);
                break;
        }
    });
    
    function renderMembers(members) {
        if (members.length === 0) {
            membersContainer.innerHTML = '<div class="empty-state">No team members online</div>';
            return;
        }
        
        membersContainer.innerHTML = members.map(member => `
            <div class="member-item">
                <div class="member-status ${member.status}"></div>
                <div class="member-info">
                    <div class="member-name">${escapeHtml(member.username)}</div>
                    <div class="member-task">${escapeHtml(member.currentTask || 'No task assigned')}</div>
                </div>
            </div>
        `).join('');
    }
    
    function showError(message) {
        membersContainer.innerHTML = `<div class="empty-state">Error: ${escapeHtml(message)}</div>`;
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