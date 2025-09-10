package com.aicache.plugin.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.diagnostic.Logger;
import com.aicache.plugin.services.AicacheService;

public class RefreshCacheAction extends AnAction {
    private static final Logger LOG = Logger.getInstance(RefreshCacheAction.class);
    
    @Override
    public void actionPerformed(AnActionEvent e) {
        AicacheService service = AicacheService.getInstance();
        if (!service.isInitialized()) {
            Messages.showMessageDialog("aicache service not initialized", "aicache", Messages.getErrorIcon());
            return;
        }
        
        try {
            // For now, just reinitialize the service
            service.initialize();
            Messages.showMessageDialog("Cache refreshed successfully", "aicache", Messages.getInformationIcon());
        } catch (Exception ex) {
            LOG.error("Error refreshing cache", ex);
            Messages.showMessageDialog("Error refreshing cache: " + ex.getMessage(), "aicache", Messages.getErrorIcon());
        }
    }
}