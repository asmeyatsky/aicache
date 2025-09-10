package com.aicache.plugin;

import com.intellij.openapi.application.ApplicationManager;
import com.intellij.openapi.components.ApplicationComponent;
import com.intellij.openapi.diagnostic.Logger;
import com.aicache.plugin.services.AicacheService;
import org.jetbrains.annotations.NotNull;

public class AicachePlugin implements ApplicationComponent {
    private static final Logger LOG = Logger.getInstance(AicachePlugin.class);
    
    public AicachePlugin() {
        LOG.info("aicache plugin initialized");
    }
    
    @Override
    public void initComponent() {
        LOG.info("aicache plugin component initialized");
        
        // Initialize the aicache service
        AicacheService service = ApplicationManager.getApplication().getService(AicacheService.class);
        if (service != null) {
            service.initialize();
        }
    }
    
    @Override
    public void disposeComponent() {
        LOG.info("aicache plugin component disposed");
    }
    
    @Override
    public @NotNull String getComponentName() {
        return "AicachePlugin";
    }
}