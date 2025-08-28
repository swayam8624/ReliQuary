// Package reliquary provides an Enterprise Go SDK for integrating with
// the ReliQuary multi-agent consensus and security platform.
//
// Features:
// - Authentication and authorization
// - Multi-agent consensus operations
// - Zero-knowledge proof generation
// - Cross-chain interactions
// - AI/ML enhanced decisions
// - Observability and monitoring
// - Enterprise security controls
package reliquary

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// ConsensusType represents the type of consensus operation
type ConsensusType string

const (
	AccessRequest      ConsensusType = "access_request"
	GovernanceDecision ConsensusType = "governance_decision"
	EmergencyResponse  ConsensusType = "emergency_response"
	SecurityValidation ConsensusType = "security_validation"
)

// DecisionStrategy represents AI/ML decision optimization strategies
type DecisionStrategy string

const (
	Conservative DecisionStrategy = "conservative"
	Balanced     DecisionStrategy = "balanced"
	Aggressive   DecisionStrategy = "aggressive"
	Adaptive     DecisionStrategy = "adaptive"
)

// AuthCredentials contains authentication information
type AuthCredentials struct {
	Username      string `json:"username,omitempty"`
	Password      string `json:"password,omitempty"`
	APIKey        string `json:"api_key,omitempty"`
	AccessToken   string `json:"access_token,omitempty"`
	DIDPrivateKey string `json:"did_private_key,omitempty"`
}

// ConsensusRequest represents a multi-agent consensus request
type ConsensusRequest struct {
	RequestType    ConsensusType          `json:"request_type"`
	ContextData    map[string]interface{} `json:"context_data"`
	UserID         string                 `json:"user_id"`
	ResourcePath   string                 `json:"resource_path"`
	Priority       int                    `json:"priority"`
	TimeoutSeconds int                    `json:"timeout_seconds"`
	RequiredAgents []string               `json:"required_agents,omitempty"`
	Metadata       map[string]interface{} `json:"metadata"`
}

// ConsensusResult represents the result of a consensus operation
type ConsensusResult struct {
	RequestID           string                 `json:"request_id"`
	Decision            string                 `json:"decision"`
	ConfidenceScore     float64                `json:"confidence_score"`
	ParticipatingAgents []string               `json:"participating_agents"`
	ConsensusTimeMs     float64                `json:"consensus_time_ms"`
	DetailedVotes       map[string]interface{} `json:"detailed_votes"`
	RiskAssessment      map[string]interface{} `json:"risk_assessment"`
	Timestamp           time.Time              `json:"timestamp"`
	Success             bool                   `json:"success"`
}

// ZKProofRequest represents a zero-knowledge proof generation request
type ZKProofRequest struct {
	CircuitType   string                 `json:"circuit_type"`
	Inputs        map[string]interface{} `json:"inputs"`
	PublicSignals []string               `json:"public_signals"`
	Metadata      map[string]interface{} `json:"metadata"`
}

// ZKProofResult represents the result of zero-knowledge proof generation
type ZKProofResult struct {
	ProofID          string                 `json:"proof_id"`
	Proof            map[string]interface{} `json:"proof"`
	PublicSignals    []string               `json:"public_signals"`
	VerificationKey  map[string]interface{} `json:"verification_key"`
	CircuitType      string                 `json:"circuit_type"`
	GenerationTimeMs float64                `json:"generation_time_ms"`
	Valid            bool                   `json:"valid"`
	Timestamp        time.Time              `json:"timestamp"`
}

// ClientStats represents client performance statistics
type ClientStats struct {
	TotalRequests         int64   `json:"total_requests"`
	AverageResponseTimeMs float64 `json:"average_response_time_ms"`
	ErrorCount            int64   `json:"error_count"`
	ErrorRatePercent      float64 `json:"error_rate_percent"`
	BaseURL               string  `json:"base_url"`
	Authenticated         bool    `json:"authenticated"`
}

// Client represents the ReliQuary SDK client
type Client struct {
	baseURL     string
	credentials *AuthCredentials
	timeout     time.Duration
	maxRetries  int
	httpClient  *http.Client
	logger      *log.Logger

	accessToken  string
	tokenExpires *time.Time

	// Performance tracking
	mu                sync.RWMutex
	requestCount      int64
	totalResponseTime time.Duration
	errorCount        int64
}

// ClientOption represents a configuration option for the client
type ClientOption func(*Client)

// WithTimeout sets the request timeout
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.timeout = timeout
		c.httpClient.Timeout = timeout
	}
}

// WithMaxRetries sets the maximum number of retries
func WithMaxRetries(maxRetries int) ClientOption {
	return func(c *Client) {
		c.maxRetries = maxRetries
	}
}

// WithLogger sets a custom logger
func WithLogger(logger *log.Logger) ClientOption {
	return func(c *Client) {
		c.logger = logger
	}
}

// NewClient creates a new ReliQuary client
func NewClient(baseURL string, credentials *AuthCredentials, options ...ClientOption) *Client {
	if credentials == nil {
		credentials = &AuthCredentials{}
	}

	client := &Client{
		baseURL:     strings.TrimSuffix(baseURL, "/"),
		credentials: credentials,
		timeout:     30 * time.Second,
		maxRetries:  3,
		httpClient:  &http.Client{Timeout: 30 * time.Second},
		logger:      log.New(io.Discard, "", 0), // Default to no logging
	}

	// Apply options
	for _, option := range options {
		option(client)
	}

	if client.credentials.AccessToken != "" {
		client.accessToken = client.credentials.AccessToken
	}

	return client
}

// NewClientWithAPIKey creates a client with API key authentication
func NewClientWithAPIKey(baseURL, apiKey string, options ...ClientOption) *Client {
	credentials := &AuthCredentials{APIKey: apiKey}
	return NewClient(baseURL, credentials, options...)
}

// NewClientWithCredentials creates a client with username/password authentication
func NewClientWithCredentials(baseURL, username, password string, options ...ClientOption) *Client {
	credentials := &AuthCredentials{Username: username, Password: password}
	return NewClient(baseURL, credentials, options...)
}

// Connect establishes connection and authenticates with the ReliQuary platform
func (c *Client) Connect(ctx context.Context) error {
	if c.accessToken == "" {
		if err := c.authenticate(ctx); err != nil {
			return fmt.Errorf("authentication failed: %w", err)
		}
	}
	c.logger.Println("Connected to ReliQuary platform")
	return nil
}

// Disconnect closes the connection to the ReliQuary platform
func (c *Client) Disconnect() {
	c.accessToken = ""
	c.tokenExpires = nil
	c.logger.Println("Disconnected from ReliQuary platform")
}

// authenticate performs authentication with the ReliQuary platform
func (c *Client) authenticate(ctx context.Context) error {
	if c.credentials.APIKey != "" {
		// API key authentication
		c.accessToken = c.credentials.APIKey
		return nil
	}

	if c.credentials.Username != "" && c.credentials.Password != "" {
		// Username/password authentication
		authData := map[string]string{
			"username": c.credentials.Username,
			"password": c.credentials.Password,
		}

		var response map[string]interface{}
		if err := c.makeRequest(ctx, "POST", "/auth/login", authData, &response); err != nil {
			return err
		}

		accessToken, ok := response["access_token"].(string)
		if !ok {
			return fmt.Errorf("invalid access token in response")
		}
		c.accessToken = accessToken

		// Calculate token expiration
		if expiresIn, ok := response["expires_in"].(float64); ok {
			expiry := time.Now().Add(time.Duration(expiresIn) * time.Second)
			c.tokenExpires = &expiry
		}

		return nil
	}

	if c.credentials.DIDPrivateKey != "" {
		// DID-based authentication
		return fmt.Errorf("DID authentication not yet implemented")
	}

	return fmt.Errorf("no valid authentication credentials provided")
}

// getHeaders returns the request headers with authentication
func (c *Client) getHeaders() map[string]string {
	headers := map[string]string{
		"Content-Type": "application/json",
		"User-Agent":   "ReliQuary-Go-SDK/1.0.0",
	}

	if c.accessToken != "" {
		headers["Authorization"] = "Bearer " + c.accessToken
	}

	return headers
}

// makeRequest makes an authenticated API request with retries
func (c *Client) makeRequest(ctx context.Context, method, endpoint string, data interface{}, result interface{}) error {
	url := c.baseURL + endpoint

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		startTime := time.Now()

		if err := c.performRequest(ctx, method, url, data, result); err != nil {
			responseTime := time.Since(startTime)
			c.updateStats(responseTime, true)

			// Check for 401 and retry authentication
			if strings.Contains(err.Error(), "401") && attempt == 0 {
				if authErr := c.authenticate(ctx); authErr != nil {
					return fmt.Errorf("re-authentication failed: %w", authErr)
				}
				continue
			}

			c.logger.Printf("Request attempt %d failed: %v", attempt+1, err)

			if attempt == c.maxRetries {
				return err
			}

			// Exponential backoff
			backoff := time.Duration(1<<uint(attempt)) * time.Second
			select {
			case <-time.After(backoff):
			case <-ctx.Done():
				return ctx.Err()
			}
			continue
		}

		responseTime := time.Since(startTime)
		c.updateStats(responseTime, false)
		c.logger.Printf("%s %s -> Success (%v)", method, endpoint, responseTime)
		return nil
	}

	return fmt.Errorf("all retry attempts failed")
}

// performRequest performs a single HTTP request
func (c *Client) performRequest(ctx context.Context, method, url string, data interface{}, result interface{}) error {
	var body io.Reader
	if data != nil {
		jsonData, err := json.Marshal(data)
		if err != nil {
			return fmt.Errorf("failed to marshal request data: %w", err)
		}
		body = bytes.NewBuffer(jsonData)
	}

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Add headers
	for key, value := range c.getHeaders() {
		req.Header.Set(key, value)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(bodyBytes))
	}

	if result != nil {
		if err := json.NewDecoder(resp.Body).Decode(result); err != nil {
			return fmt.Errorf("failed to decode response: %w", err)
		}
	}

	return nil
}

// updateStats updates performance statistics
func (c *Client) updateStats(responseTime time.Duration, isError bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.requestCount++
	c.totalResponseTime += responseTime
	if isError {
		c.errorCount++
	}
}

// Health and Status Methods

// HealthCheck checks system health
func (c *Client) HealthCheck(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", "/health", nil, &result)
	return result, err
}

// GetSystemStatus gets comprehensive system status
func (c *Client) GetSystemStatus(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", "/status", nil, &result)
	return result, err
}

// Authentication Methods

// RefreshToken refreshes the authentication token
func (c *Client) RefreshToken(ctx context.Context) (string, error) {
	var response map[string]interface{}
	if err := c.makeRequest(ctx, "POST", "/auth/refresh", nil, &response); err != nil {
		return "", err
	}

	accessToken, ok := response["access_token"].(string)
	if !ok {
		return "", fmt.Errorf("invalid access token in response")
	}

	c.accessToken = accessToken
	return accessToken, nil
}

// GetUserProfile gets the current user profile
func (c *Client) GetUserProfile(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", "/auth/profile", nil, &result)
	return result, err
}

// Multi-Agent Consensus Methods

// SubmitConsensusRequest submits a request for multi-agent consensus
func (c *Client) SubmitConsensusRequest(ctx context.Context, request *ConsensusRequest) (*ConsensusResult, error) {
	var result ConsensusResult
	err := c.makeRequest(ctx, "POST", "/consensus/submit", request, &result)
	return &result, err
}

// GetConsensusResult gets consensus result by request ID
func (c *Client) GetConsensusResult(ctx context.Context, requestID string) (*ConsensusResult, error) {
	var result ConsensusResult
	err := c.makeRequest(ctx, "GET", "/consensus/result/"+requestID, nil, &result)
	return &result, err
}

// ListActiveConsensus lists active consensus operations
func (c *Client) ListActiveConsensus(ctx context.Context) ([]map[string]interface{}, error) {
	var response map[string]interface{}
	if err := c.makeRequest(ctx, "GET", "/consensus/active", nil, &response); err != nil {
		return nil, err
	}

	activeConsensus, ok := response["active_consensus"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid active_consensus in response")
	}

	result := make([]map[string]interface{}, len(activeConsensus))
	for i, item := range activeConsensus {
		if consensus, ok := item.(map[string]interface{}); ok {
			result[i] = consensus
		}
	}

	return result, nil
}

// Zero-Knowledge Proof Methods

// GenerateZKProof generates a zero-knowledge proof
func (c *Client) GenerateZKProof(ctx context.Context, request *ZKProofRequest) (*ZKProofResult, error) {
	var result ZKProofResult
	err := c.makeRequest(ctx, "POST", "/zk/generate", request, &result)
	return &result, err
}

// VerifyZKProof verifies a zero-knowledge proof
func (c *Client) VerifyZKProof(ctx context.Context, proofID string, proof map[string]interface{}, publicSignals []string) (bool, error) {
	requestData := map[string]interface{}{
		"proof_id":       proofID,
		"proof":          proof,
		"public_signals": publicSignals,
	}

	var response map[string]interface{}
	if err := c.makeRequest(ctx, "POST", "/zk/verify", requestData, &response); err != nil {
		return false, err
	}

	valid, ok := response["valid"].(bool)
	if !ok {
		return false, fmt.Errorf("invalid valid field in response")
	}

	return valid, nil
}

// AI/ML Enhanced Decision Methods

// GetAIEnhancedDecision gets an AI/ML enhanced decision
func (c *Client) GetAIEnhancedDecision(ctx context.Context, decisionType string, userData, contextData map[string]interface{}, strategy DecisionStrategy) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"decision_type":         decisionType,
		"user_data":             userData,
		"context_data":          contextData,
		"optimization_strategy": string(strategy),
	}

	var result map[string]interface{}
	err := c.makeRequest(ctx, "POST", "/ai-ml/decisions/enhance", requestData, &result)
	return result, err
}

// AnalyzeBehavioralPatterns analyzes user behavioral patterns
func (c *Client) AnalyzeBehavioralPatterns(ctx context.Context, userID string, timeRangeHours int) (map[string]interface{}, error) {
	endpoint := fmt.Sprintf("/ai-ml/analytics/patterns?user_id=%s&time_range_hours=%d",
		url.QueryEscape(userID), timeRangeHours)

	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", endpoint, nil, &result)
	return result, err
}

// Cross-Chain Methods

// SubmitCrossChainTransaction submits a cross-chain transaction
func (c *Client) SubmitCrossChainTransaction(ctx context.Context, sourceChain, targetChain string, transactionData map[string]interface{}) (map[string]interface{}, error) {
	requestData := map[string]interface{}{
		"source_chain":     sourceChain,
		"target_chain":     targetChain,
		"transaction_data": transactionData,
	}

	var result map[string]interface{}
	err := c.makeRequest(ctx, "POST", "/crosschain/submit", requestData, &result)
	return result, err
}

// GetCrossChainStatus gets cross-chain transaction status
func (c *Client) GetCrossChainStatus(ctx context.Context, transactionID string) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", "/crosschain/status/"+transactionID, nil, &result)
	return result, err
}

// Observability Methods

// RecordMetric records a custom metric
func (c *Client) RecordMetric(ctx context.Context, name string, value float64, labels map[string]string) (map[string]interface{}, error) {
	if labels == nil {
		labels = make(map[string]string)
	}

	requestData := map[string]interface{}{
		"name":   name,
		"value":  value,
		"labels": labels,
	}

	var result map[string]interface{}
	err := c.makeRequest(ctx, "POST", "/observability/metrics/record", requestData, &result)
	return result, err
}

// GetSystemDashboard gets system dashboard data
func (c *Client) GetSystemDashboard(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", "/observability/dashboard", nil, &result)
	return result, err
}

// TriggerAlert manually triggers an alert
func (c *Client) TriggerAlert(ctx context.Context, metricName string, value float64, description string) (map[string]interface{}, error) {
	if description == "" {
		description = "SDK triggered alert"
	}

	requestData := map[string]interface{}{
		"metric_name": metricName,
		"value":       value,
		"description": description,
	}

	var result map[string]interface{}
	err := c.makeRequest(ctx, "POST", "/observability/alerts/trigger", requestData, &result)
	return result, err
}

// Vault and Secret Management Methods

// StoreSecret stores a secret in a vault
func (c *Client) StoreSecret(ctx context.Context, vaultID, secretName, secretValue string, metadata map[string]interface{}) (map[string]interface{}, error) {
	if metadata == nil {
		metadata = make(map[string]interface{})
	}

	requestData := map[string]interface{}{
		"vault_id":     vaultID,
		"secret_name":  secretName,
		"secret_value": secretValue,
		"metadata":     metadata,
	}

	var result map[string]interface{}
	err := c.makeRequest(ctx, "POST", "/vaults/secrets", requestData, &result)
	return result, err
}

// RetrieveSecret retrieves a secret from a vault
func (c *Client) RetrieveSecret(ctx context.Context, vaultID, secretName string) (map[string]interface{}, error) {
	endpoint := fmt.Sprintf("/vaults/secrets?vault_id=%s&secret_name=%s",
		url.QueryEscape(vaultID), url.QueryEscape(secretName))

	var result map[string]interface{}
	err := c.makeRequest(ctx, "GET", endpoint, nil, &result)
	return result, err
}

// GetClientStats returns client performance statistics
func (c *Client) GetClientStats() *ClientStats {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var avgResponseTime float64
	if c.requestCount > 0 {
		avgResponseTime = float64(c.totalResponseTime.Nanoseconds()) / float64(c.requestCount) / 1e6
	}

	var errorRate float64
	if c.requestCount > 0 {
		errorRate = float64(c.errorCount) / float64(c.requestCount) * 100
	}

	return &ClientStats{
		TotalRequests:         c.requestCount,
		AverageResponseTimeMs: avgResponseTime,
		ErrorCount:            c.errorCount,
		ErrorRatePercent:      errorRate,
		BaseURL:               c.baseURL,
		Authenticated:         c.accessToken != "",
	}
}

// Convenience functions

// QuickConsensus performs a quick consensus operation
func QuickConsensus(ctx context.Context, baseURL, apiKey string, requestType ConsensusType, contextData map[string]interface{}, userID, resourcePath string) (*ConsensusResult, error) {
	client := NewClientWithAPIKey(baseURL, apiKey)
	if err := client.Connect(ctx); err != nil {
		return nil, err
	}
	defer client.Disconnect()

	request := &ConsensusRequest{
		RequestType:    requestType,
		ContextData:    contextData,
		UserID:         userID,
		ResourcePath:   resourcePath,
		Priority:       5,
		TimeoutSeconds: 30,
		Metadata:       make(map[string]interface{}),
	}

	return client.SubmitConsensusRequest(ctx, request)
}

// QuickAIDecision performs a quick AI-enhanced decision
func QuickAIDecision(ctx context.Context, baseURL, apiKey string, decisionType string, userData, contextData map[string]interface{}) (map[string]interface{}, error) {
	client := NewClientWithAPIKey(baseURL, apiKey)
	if err := client.Connect(ctx); err != nil {
		return nil, err
	}
	defer client.Disconnect()

	return client.GetAIEnhancedDecision(ctx, decisionType, userData, contextData, Balanced)
}
