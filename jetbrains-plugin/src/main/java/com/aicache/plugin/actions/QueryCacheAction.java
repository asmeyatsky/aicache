package com.aicache.plugin.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.diagnostic.Logger;
import com.aicache.plugin.services.AicacheService;
import com.google.gson.JsonObject;

public class QueryCacheAction extends AnAction {
    private static final Logger LOG = Logger.getInstance(QueryCacheAction.class);
    
    @Override
    public void actionPerformed(AnActionEvent e) {
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        if (editor == null) {
            Messages.showMessageDialog("No editor found", "aicache", Messages.getErrorIcon());
            return;
        }
        
        AicacheService service = AicacheService.getInstance();
        if (!service.isInitialized()) {
            Messages.showMessageDialog("aicache service not initialized", "aicache", Messages.getErrorIcon());
            return;
        }
        
        // Get selected text or current line
        String selectedText = editor.getSelectionModel().getSelectedText();
        if (selectedText == null || selectedText.isEmpty()) {
            int offset = editor.getCaretModel().getOffset();
            int line = editor.getDocument().getLineNumber(offset);
            selectedText = editor.getDocument().getText().substring(
                editor.getDocument().getLineStartOffset(line),
                editor.getDocument().getLineEndOffset(line)
            ).trim();
        }
        
        if (selectedText.isEmpty()) {
            selectedText = Messages.showInputDialog("Enter your query:", "aicache Query", Messages.getQuestionIcon());
            if (selectedText == null || selectedText.isEmpty()) {
                return;
            }
        }
        
        try {
            // Build context
            JsonObject context = new JsonObject();
            context.addProperty("language", "java"); // Simplified for now
            context.addProperty("file", editor.getVirtualFile().getName());
            
            String response = service.queryCache(selectedText, context);
            if (response != null) {
                Messages.showMessageDialog(response, "aicache Response", Messages.getInformationIcon());
            } else {
                Messages.showMessageDialog("No response from cache", "aicache", Messages.getWarningIcon());
            }
        } catch (Exception ex) {
            LOG.error("Error querying cache", ex);
            Messages.showMessageDialog("Error querying cache: " + ex.getMessage(), "aicache", Messages.getErrorIcon());
        }
    }
    
    @Override
    public void update(AnActionEvent e) {
        // Enable the action only when there's an editor
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        e.getPresentation().setEnabledAndVisible(editor != null);
    }
}