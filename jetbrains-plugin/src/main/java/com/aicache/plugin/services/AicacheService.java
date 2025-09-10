package com.aicache.plugin.services;

import com.intellij.openapi.application.ApplicationManager;
import com.intellij.openapi.components.Service;
import com.intellij.openapi.diagnostic.Logger;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.IOException;

@Service
public final class AicacheService {
    private static final Logger LOG = Logger.getInstance(AicacheService.class);
    private static final String DEFAULT_SERVICE_URL = "http://localhost:8080";
    
    private final HttpClient httpClient;
    private final Gson gson;
    private boolean initialized = false;
    
    public AicacheService() {
        this.httpClient = HttpClientBuilder.create().build();
        this.gson = new Gson();
    }
    
    public void initialize() {
        try {
            // Test connection to aicache service
            HttpGet request = new HttpGet(DEFAULT_SERVICE_URL + "/health");
            HttpResponse response = httpClient.execute(request);
            
            if (response.getStatusLine().getStatusCode() == 200) {
                initialized = true;
                LOG.info("aicache service initialized successfully");
            } else {
                LOG.warn("aicache service initialization failed: " + response.getStatusLine().getStatusCode());
            }
        } catch (IOException e) {
            LOG.error("Failed to connect to aicache service", e);
        }
    }
    
    public String queryCache(String prompt, JsonObject context) {
        if (!initialized) {
            LOG.warn("aicache service not initialized");
            return null;
        }
        
        try {
            HttpPost request = new HttpPost(DEFAULT_SERVICE_URL + "/cache/query");
            request.setHeader("Content-Type", "application/json");
            
            JsonObject requestBody = new JsonObject();
            requestBody.addProperty("prompt", prompt);
            requestBody.add("context", context);
            
            request.setEntity(new StringEntity(gson.toJson(requestBody)));
            
            HttpResponse response = httpClient.execute(request);
            
            if (response.getStatusLine().getStatusCode() == 200) {
                String responseBody = EntityUtils.toString(response.getEntity());
                JsonObject responseObject = gson.fromJson(responseBody, JsonObject.class);
                return responseObject.get("response").getAsString();
            } else {
                LOG.warn("Cache query failed: " + response.getStatusLine().getStatusCode());
                return null;
            }
        } catch (IOException e) {
            LOG.error("Failed to query cache", e);
            return null;
        }
    }
    
    public boolean isInitialized() {
        return initialized;
    }
    
    public static AicacheService getInstance() {
        return ApplicationManager.getApplication().getService(AicacheService.class);
    }
}