/**
 * ReliQuary Enterprise Java SDK
 * 
 * This SDK provides a comprehensive Java client for integrating with
 * the ReliQuary multi-agent consensus and security platform.
 * 
 * Features:
 * - Authentication and authorization
 * - Multi-agent consensus operations
 * - Zero-knowledge proof generation
 * - Cross-chain interactions
 * - AI/ML enhanced decisions
 * - Observability and monitoring
 * - Enterprise security controls
 */

package io.reliquary.sdk;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.logging.Logger;

public class ReliQuaryClient implements AutoCloseable {

    // Enums
    public enum ConsensusType {
        ACCESS_REQUEST("access_request"),
        GOVERNANCE_DECISION("governance_decision"),
        EMERGENCY_RESPONSE("emergency_response"),
        SECURITY_VALIDATION("security_validation");

        private final String value;

        ConsensusType(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    public enum DecisionStrategy {
        CONSERVATIVE("conservative"),
        BALANCED("balanced"),
        AGGRESSIVE("aggressive"),
        ADAPTIVE("adaptive");

        private final String value;

        DecisionStrategy(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    // Data classes
    public static class AuthCredentials {
        private String username;
        private String password;
        private String apiKey;
        private String accessToken;
        private String didPrivateKey;

        // Constructors
        public AuthCredentials() {
        }

        public AuthCredentials(String apiKey) {
            this.apiKey = apiKey;
        }

        public AuthCredentials(String username, String password) {
            this.username = username;
            this.password = password;
        }

        // Getters and setters
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getApiKey() {
            return apiKey;
        }

        public void setApiKey(String apiKey) {
            this.apiKey = apiKey;
        }

        public String getAccessToken() {
            return accessToken;
        }

        public void setAccessToken(String accessToken) {
            this.accessToken = accessToken;
        }

        public String getDidPrivateKey() {
            return didPrivateKey;
        }

        public void setDidPrivateKey(String didPrivateKey) {
            this.didPrivateKey = didPrivateKey;
        }
    }

    public static class ConsensusRequest {
        @JsonProperty("request_type")
        private ConsensusType requestType;

        @JsonProperty("context_data")
        private Map<String, Object> contextData;

        @JsonProperty("user_id")
        private String userId;

        @JsonProperty("resource_path")
        private String resourcePath;

        private int priority = 5;

        @JsonProperty("timeout_seconds")
        private int timeoutSeconds = 30;

        @JsonProperty("required_agents")
        private List<String> requiredAgents;

        private Map<String, Object> metadata = new HashMap<>();

        // Constructors
        public ConsensusRequest() {
        }

        public ConsensusRequest(ConsensusType requestType, Map<String, Object> contextData,
                String userId, String resourcePath) {
            this.requestType = requestType;
            this.contextData = contextData;
            this.userId = userId;
            this.resourcePath = resourcePath;
        }

        // Getters and setters
        public ConsensusType getRequestType() {
            return requestType;
        }

        public void setRequestType(ConsensusType requestType) {
            this.requestType = requestType;
        }

        public Map<String, Object> getContextData() {
            return contextData;
        }

        public void setContextData(Map<String, Object> contextData) {
            this.contextData = contextData;
        }

        public String getUserId() {
            return userId;
        }

        public void setUserId(String userId) {
            this.userId = userId;
        }

        public String getResourcePath() {
            return resourcePath;
        }

        public void setResourcePath(String resourcePath) {
            this.resourcePath = resourcePath;
        }

        public int getPriority() {
            return priority;
        }

        public void setPriority(int priority) {
            this.priority = priority;
        }

        public int getTimeoutSeconds() {
            return timeoutSeconds;
        }

        public void setTimeoutSeconds(int timeoutSeconds) {
            this.timeoutSeconds = timeoutSeconds;
        }

        public List<String> getRequiredAgents() {
            return requiredAgents;
        }

        public void setRequiredAgents(List<String> requiredAgents) {
            this.requiredAgents = requiredAgents;
        }

        public Map<String, Object> getMetadata() {
            return metadata;
        }

        public void setMetadata(Map<String, Object> metadata) {
            this.metadata = metadata;
        }
    }

    public static class ConsensusResult {
        @JsonProperty("request_id")
        private String requestId;

        private String decision;

        @JsonProperty("confidence_score")
        private double confidenceScore;

        @JsonProperty("participating_agents")
        private List<String> participatingAgents;

        @JsonProperty("consensus_time_ms")
        private double consensusTimeMs;

        @JsonProperty("detailed_votes")
        private Map<String, Object> detailedVotes;

        @JsonProperty("risk_assessment")
        private Map<String, Object> riskAssessment;

        private Instant timestamp;
        private boolean success;

        // Getters and setters
        public String getRequestId() {
            return requestId;
        }

        public void setRequestId(String requestId) {
            this.requestId = requestId;
        }

        public String getDecision() {
            return decision;
        }

        public void setDecision(String decision) {
            this.decision = decision;
        }

        public double getConfidenceScore() {
            return confidenceScore;
        }

        public void setConfidenceScore(double confidenceScore) {
            this.confidenceScore = confidenceScore;
        }

        public List<String> getParticipatingAgents() {
            return participatingAgents;
        }

        public void setParticipatingAgents(List<String> participatingAgents) {
            this.participatingAgents = participatingAgents;
        }

        public double getConsensusTimeMs() {
            return consensusTimeMs;
        }

        public void setConsensusTimeMs(double consensusTimeMs) {
            this.consensusTimeMs = consensusTimeMs;
        }

        public Map<String, Object> getDetailedVotes() {
            return detailedVotes;
        }

        public void setDetailedVotes(Map<String, Object> detailedVotes) {
            this.detailedVotes = detailedVotes;
        }

        public Map<String, Object> getRiskAssessment() {
            return riskAssessment;
        }

        public void setRiskAssessment(Map<String, Object> riskAssessment) {
            this.riskAssessment = riskAssessment;
        }

        public Instant getTimestamp() {
            return timestamp;
        }

        public void setTimestamp(Instant timestamp) {
            this.timestamp = timestamp;
        }

        public boolean isSuccess() {
            return success;
        }

        public void setSuccess(boolean success) {
            this.success = success;
        }
    }

    public static class ZKProofRequest {
        @JsonProperty("circuit_type")
        private String circuitType;

        private Map<String, Object> inputs;

        @JsonProperty("public_signals")
        private List<String> publicSignals;

        private Map<String, Object> metadata = new HashMap<>();

        public ZKProofRequest() {
        }

        public ZKProofRequest(String circuitType, Map<String, Object> inputs, List<String> publicSignals) {
            this.circuitType = circuitType;
            this.inputs = inputs;
            this.publicSignals = publicSignals;
        }

        // Getters and setters
        public String getCircuitType() {
            return circuitType;
        }

        public void setCircuitType(String circuitType) {
            this.circuitType = circuitType;
        }

        public Map<String, Object> getInputs() {
            return inputs;
        }

        public void setInputs(Map<String, Object> inputs) {
            this.inputs = inputs;
        }

        public List<String> getPublicSignals() {
            return publicSignals;
        }

        public void setPublicSignals(List<String> publicSignals) {
            this.publicSignals = publicSignals;
        }

        public Map<String, Object> getMetadata() {
            return metadata;
        }

        public void setMetadata(Map<String, Object> metadata) {
            this.metadata = metadata;
        }
    }

    public static class ClientStats {
        private long totalRequests;
        private double averageResponseTimeMs;
        private long errorCount;
        private double errorRatePercent;
        private String baseUrl;
        private boolean authenticated;

        public ClientStats(long totalRequests, double averageResponseTimeMs, long errorCount,
                double errorRatePercent, String baseUrl, boolean authenticated) {
            this.totalRequests = totalRequests;
            this.averageResponseTimeMs = averageResponseTimeMs;
            this.errorCount = errorCount;
            this.errorRatePercent = errorRatePercent;
            this.baseUrl = baseUrl;
            this.authenticated = authenticated;
        }

        // Getters
        public long getTotalRequests() {
            return totalRequests;
        }

        public double getAverageResponseTimeMs() {
            return averageResponseTimeMs;
        }

        public long getErrorCount() {
            return errorCount;
        }

        public double getErrorRatePercent() {
            return errorRatePercent;
        }

        public String getBaseUrl() {
            return baseUrl;
        }

        public boolean isAuthenticated() {
            return authenticated;
        }
    }

    // Client implementation
    private static final Logger logger = Logger.getLogger(ReliQuaryClient.class.getName());

    private final String baseUrl;
    private final AuthCredentials credentials;
    private final Duration timeout;
    private final int maxRetries;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    private String accessToken;
    private Instant tokenExpires;

    // Performance tracking
    private long requestCount = 0;
    private long totalResponseTime = 0;
    private long errorCount = 0;

    public ReliQuaryClient(String baseUrl, AuthCredentials credentials) {
        this(baseUrl, credentials, Duration.ofSeconds(30), 3);
    }

    public ReliQuaryClient(String baseUrl, AuthCredentials credentials, Duration timeout, int maxRetries) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.credentials = credentials != null ? credentials : new AuthCredentials();
        this.timeout = timeout;
        this.maxRetries = maxRetries;

        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(timeout)
                .build();

        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());

        if (this.credentials.getAccessToken() != null) {
            this.accessToken = this.credentials.getAccessToken();
        }
    }

    /**
     * Connect and authenticate with ReliQuary platform
     */
    public CompletableFuture<Void> connect() {
        return CompletableFuture.runAsync(() -> {
            if (accessToken == null) {
                try {
                    authenticate();
                } catch (Exception e) {
                    throw new CompletionException(e);
                }
            }
            logger.info("Connected to ReliQuary platform");
        });
    }

    /**
     * Disconnect from ReliQuary platform
     */
    public CompletableFuture<Void> disconnect() {
        return CompletableFuture.runAsync(() -> {
            accessToken = null;
            tokenExpires = null;
            logger.info("Disconnected from ReliQuary platform");
        });
    }

    /**
     * Perform authentication
     */
    private void authenticate() throws IOException, InterruptedException {
        if (credentials.getApiKey() != null) {
            // API key authentication
            accessToken = credentials.getApiKey();
        } else if (credentials.getUsername() != null && credentials.getPassword() != null) {
            // Username/password authentication
            Map<String, String> authData = new HashMap<>();
            authData.put("username", credentials.getUsername());
            authData.put("password", credentials.getPassword());

            Map<String, Object> response = makeRequest("POST", "/auth/login", authData,
                    new TypeReference<Map<String, Object>>() {
                    });
            accessToken = (String) response.get("access_token");

            // Calculate token expiration
            Integer expiresIn = (Integer) response.getOrDefault("expires_in", 3600);
            tokenExpires = Instant.now().plusSeconds(expiresIn);
        } else if (credentials.getDidPrivateKey() != null) {
            // DID-based authentication
            throw new UnsupportedOperationException("DID authentication not yet implemented");
        } else {
            throw new IllegalArgumentException("No valid authentication credentials provided");
        }
    }

    /**
     * Get request headers with authentication
     */
    private Map<String, String> getHeaders() {
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        headers.put("User-Agent", "ReliQuary-Java-SDK/1.0.0");

        if (accessToken != null) {
            headers.put("Authorization", "Bearer " + accessToken);
        }

        return headers;
    }

    /**
     * Make authenticated API request with retries
     */
    private <T> T makeRequest(String method, String endpoint, Object data, TypeReference<T> responseType)
            throws IOException, InterruptedException {

        String url = baseUrl + endpoint;
        Map<String, String> headers = getHeaders();

        for (int attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                long startTime = System.currentTimeMillis();

                HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                        .uri(URI.create(url))
                        .timeout(timeout);

                // Add headers
                for (Map.Entry<String, String> header : headers.entrySet()) {
                    requestBuilder.header(header.getKey(), header.getValue());
                }

                // Add body for POST/PUT requests
                if ("POST".equals(method) || "PUT".equals(method)) {
                    String jsonBody = objectMapper.writeValueAsString(data);
                    requestBuilder.method(method, HttpRequest.BodyPublishers.ofString(jsonBody));
                } else {
                    requestBuilder.method(method, HttpRequest.BodyPublishers.noBody());
                }

                HttpRequest request = requestBuilder.build();
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                long responseTime = System.currentTimeMillis() - startTime;
                requestCount++;
                totalResponseTime += responseTime;

                if (response.statusCode() == 401 && attempt == 0) {
                    // Token might be expired, retry authentication
                    authenticate();
                    headers = getHeaders();
                    continue;
                }

                if (response.statusCode() >= 400) {
                    throw new RuntimeException("HTTP " + response.statusCode() + ": " + response.body());
                }

                logger.fine(method + " " + endpoint + " -> " + response.statusCode() + " (" + responseTime + "ms)");
                return objectMapper.readValue(response.body(), responseType);

            } catch (Exception e) {
                errorCount++;
                logger.warning("Request attempt " + (attempt + 1) + " failed: " + e.getMessage());

                if (attempt == maxRetries) {
                    throw new RuntimeException(e);
                }

                // Exponential backoff
                try {
                    Thread.sleep((long) Math.pow(2, attempt) * 1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw ie;
                }
            }
        }

        throw new RuntimeException("All retry attempts failed");
    }

    // Health and Status Methods

    /**
     * Check system health
     */
    public CompletableFuture<Map<String, Object>> healthCheck() {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("GET", "/health", null, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Get comprehensive system status
     */
    public CompletableFuture<Map<String, Object>> getSystemStatus() {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("GET", "/status", null, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    // Authentication Methods

    /**
     * Refresh authentication token
     */
    public CompletableFuture<String> refreshToken() {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                Map<String, Object> response = makeRequest("POST", "/auth/refresh", null, typeRef);
                accessToken = (String) response.get("access_token");
                return accessToken;
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Get current user profile
     */
    public CompletableFuture<Map<String, Object>> getUserProfile() {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("GET", "/auth/profile", null, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    // Multi-Agent Consensus Methods

    /**
     * Submit request for multi-agent consensus
     */
    public CompletableFuture<ConsensusResult> submitConsensusRequest(ConsensusRequest request) {
        TypeReference<ConsensusResult> typeRef = new TypeReference<ConsensusResult>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("POST", "/consensus/submit", request, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Get consensus result by request ID
     */
    public CompletableFuture<ConsensusResult> getConsensusResult(String requestId) {
        TypeReference<ConsensusResult> typeRef = new TypeReference<ConsensusResult>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("GET", "/consensus/result/" + requestId, null, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * List active consensus operations
     */
    public CompletableFuture<List<Map<String, Object>>> listActiveConsensus() {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                Map<String, Object> response = makeRequest("GET", "/consensus/active", null, typeRef);
                return (List<Map<String, Object>>) response.get("active_consensus");
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    // Zero-Knowledge Proof Methods

    /**
     * Generate zero-knowledge proof
     */
    public CompletableFuture<Map<String, Object>> generateZKProof(ZKProofRequest request) {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                return makeRequest("POST", "/zk/generate", request, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Verify zero-knowledge proof
     */
    public CompletableFuture<Boolean> verifyZKProof(String proofId, Map<String, Object> proof,
            List<String> publicSignals) {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                Map<String, Object> requestData = new HashMap<>();
                requestData.put("proof_id", proofId);
                requestData.put("proof", proof);
                requestData.put("public_signals", publicSignals);

                Map<String, Object> response = makeRequest("POST", "/zk/verify", requestData, typeRef);
                return (Boolean) response.get("valid");
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    // AI/ML Enhanced Decision Methods

    /**
     * Get AI/ML enhanced decision
     */
    public CompletableFuture<Map<String, Object>> getAIEnhancedDecision(
            String decisionType,
            Map<String, Object> userData,
            Map<String, Object> contextData,
            DecisionStrategy strategy) {

        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                Map<String, Object> requestData = new HashMap<>();
                requestData.put("decision_type", decisionType);
                requestData.put("user_data", userData);
                requestData.put("context_data", contextData);
                requestData.put("optimization_strategy", strategy.getValue());

                return makeRequest("POST", "/ai-ml/decisions/enhance", requestData, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Record custom metric
     */
    public CompletableFuture<Map<String, Object>> recordMetric(String name, double value, Map<String, String> labels) {
        TypeReference<Map<String, Object>> typeRef = new TypeReference<Map<String, Object>>() {
        };
        return CompletableFuture.supplyAsync(() -> {
            try {
                Map<String, Object> requestData = new HashMap<>();
                requestData.put("name", name);
                requestData.put("value", value);
                requestData.put("labels", labels != null ? labels : new HashMap<>());

                return makeRequest("POST", "/observability/metrics/record", requestData, typeRef);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        });
    }

    /**
     * Get client performance statistics
     */
    public ClientStats getClientStats() {
        double avgResponseTime = totalResponseTime / (double) Math.max(requestCount, 1);
        double errorRate = errorCount / (double) Math.max(requestCount, 1) * 100;

        return new ClientStats(
                requestCount,
                avgResponseTime,
                errorCount,
                errorRate,
                baseUrl,
                accessToken != null);
    }

    @Override
    public void close() {
        disconnect().join();
    }

    // Static factory methods

    /**
     * Create client with API key authentication
     */
    public static ReliQuaryClient withApiKey(String baseUrl, String apiKey) {
        AuthCredentials credentials = new AuthCredentials(apiKey);
        return new ReliQuaryClient(baseUrl, credentials);
    }

    /**
     * Create client with username/password authentication
     */
    public static ReliQuaryClient withCredentials(String baseUrl, String username, String password) {
        AuthCredentials credentials = new AuthCredentials(username, password);
        return new ReliQuaryClient(baseUrl, credentials);
    }
}

// Example usage class
class ReliQuaryExample {
    public static void main(String[] args) {
        ReliQuaryClient client = ReliQuaryClient.withApiKey("http://localhost:8000", "your-api-key");

        client.connect().thenCompose(v -> {
            // Health check
            return client.healthCheck();
        }).thenCompose(health -> {
            System.out.println("System health: " + health);

            // Submit consensus request
            ConsensusRequest request = new ConsensusRequest();
            request.setRequestType(ReliQuaryClient.ConsensusType.ACCESS_REQUEST);
            request.setContextData(Map.of("resource_sensitivity", "high"));
            request.setUserId("user123");
            request.setResourcePath("/secure/data");

            return client.submitConsensusRequest(request);
        }).thenCompose(result -> {
            System.out.println("Consensus decision: " + result.getDecision());

            // Record metric
            return client.recordMetric("sdk_usage", 1.0, Map.of("operation", "consensus"));
        }).thenRun(() -> {
            // Get client statistics
            ReliQuaryClient.ClientStats stats = client.getClientStats();
            System.out.println("Client stats: " + stats.getTotalRequests() + " requests, " +
                    stats.getAverageResponseTimeMs() + "ms avg response time");
        }).exceptionally(throwable -> {
            throwable.printStackTrace();
            return null;
        }).whenComplete((result, throwable) -> {
            client.close();
        });
    }
}