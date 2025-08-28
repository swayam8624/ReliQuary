/**
 * ReliQuary Enterprise JavaScript/TypeScript SDK
 * 
 * This SDK provides a comprehensive JavaScript/TypeScript client for integrating
 * with the ReliQuary multi-agent consensus and security platform.
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

// Type definitions
export enum ConsensusType {
    ACCESS_REQUEST = "access_request",
    GOVERNANCE_DECISION = "governance_decision", 
    EMERGENCY_RESPONSE = "emergency_response",
    SECURITY_VALIDATION = "security_validation"
}

export enum DecisionStrategy {
    CONSERVATIVE = "conservative",
    BALANCED = "balanced",
    AGGRESSIVE = "aggressive",
    ADAPTIVE = "adaptive"
}

export interface AuthCredentials {
    username?: string;
    password?: string;
    apiKey?: string;
    accessToken?: string;
    didPrivateKey?: string;
}

export interface ConsensusRequest {
    requestType: ConsensusType;
    contextData: Record<string, any>;
    userId: string;
    resourcePath: string;
    priority?: number;
    timeoutSeconds?: number;
    requiredAgents?: string[];
    metadata?: Record<string, any>;
}

export interface ConsensusResult {
    requestId: string;
    decision: string;
    confidenceScore: number;
    participatingAgents: string[];
    consensusTimeMs: number;
    detailedVotes: Record<string, any>;
    riskAssessment: Record<string, any>;
    timestamp: Date;
    success: boolean;
}

export interface ZKProofRequest {
    circuitType: string;
    inputs: Record<string, any>;
    publicSignals: string[];
    metadata?: Record<string, any>;
}

export interface ZKProofResult {
    proofId: string;
    proof: Record<string, any>;
    publicSignals: string[];
    verificationKey: Record<string, any>;
    circuitType: string;
    generationTimeMs: number;
    valid: boolean;
    timestamp: Date;
}

export interface ClientConfig {
    baseUrl?: string;
    credentials?: AuthCredentials;
    timeout?: number;
    maxRetries?: number;
    logger?: Console;
}

export interface ClientStats {
    totalRequests: number;
    averageResponseTimeMs: number;
    errorCount: number;
    errorRatePercent: number;
    baseUrl: string;
    authenticated: boolean;
}

/**
 * Enterprise ReliQuary JavaScript/TypeScript SDK Client
 */
export class ReliQuaryClient {
    private baseUrl: string;
    private credentials: AuthCredentials;
    private timeout: number;
    private maxRetries: number;
    private logger: Console;
    
    private accessToken?: string;
    private tokenExpires?: Date;
    
    // Performance tracking
    private requestCount = 0;
    private totalResponseTime = 0;
    private errorCount = 0;

    constructor(config: ClientConfig = {}) {
        this.baseUrl = config.baseUrl?.replace(/\/$/, '') || 'http://localhost:8000';
        this.credentials = config.credentials || {};
        this.timeout = config.timeout || 30000;
        this.maxRetries = config.maxRetries || 3;
        this.logger = config.logger || console;
        
        if (this.credentials.accessToken) {
            this.accessToken = this.credentials.accessToken;
        }
    }

    /**
     * Connect and authenticate with ReliQuary platform
     */
    async connect(): Promise<void> {
        if (!this.accessToken) {
            await this.authenticate();
        }
        this.logger.log('Connected to ReliQuary platform');
    }

    /**
     * Disconnect from ReliQuary platform
     */
    async disconnect(): Promise<void> {
        this.accessToken = undefined;
        this.tokenExpires = undefined;
        this.logger.log('Disconnected from ReliQuary platform');
    }

    /**
     * Perform authentication
     */
    private async authenticate(): Promise<void> {
        if (this.credentials.apiKey) {
            // API key authentication
            this.accessToken = this.credentials.apiKey;
        } else if (this.credentials.username && this.credentials.password) {
            // Username/password authentication
            const authData = {
                username: this.credentials.username,
                password: this.credentials.password
            };
            
            const response = await this.makeRequest('POST', '/auth/login', authData);
            this.accessToken = response.access_token;
            
            // Calculate token expiration
            const expiresIn = response.expires_in || 3600;
            this.tokenExpires = new Date(Date.now() + expiresIn * 1000);
        } else if (this.credentials.didPrivateKey) {
            // DID-based authentication
            // This would implement DID authentication flow
            throw new Error('DID authentication not yet implemented');
        } else {
            throw new Error('No valid authentication credentials provided');
        }
    }

    /**
     * Get request headers with authentication
     */
    private getHeaders(): Record<string, string> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'User-Agent': 'ReliQuary-JS-SDK/1.0.0'
        };

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        return headers;
    }

    /**
     * Make authenticated API request with retries
     */
    private async makeRequest(
        method: string, 
        endpoint: string, 
        data?: any,
        params?: Record<string, string>
    ): Promise<any> {
        const url = new URL(endpoint, this.baseUrl);
        
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                url.searchParams.append(key, value);
            });
        }

        const headers = this.getHeaders();

        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
            try {
                const startTime = Date.now();
                
                const requestInit: RequestInit = {
                    method,
                    headers,
                    ...(data && { body: JSON.stringify(data) })
                };

                // Add timeout using AbortController
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                requestInit.signal = controller.signal;

                const response = await fetch(url.toString(), requestInit);
                clearTimeout(timeoutId);

                const responseTime = Date.now() - startTime;
                this.requestCount++;
                this.totalResponseTime += responseTime;

                if (response.status === 401 && attempt === 0) {
                    // Token might be expired, retry authentication
                    await this.authenticate();
                    continue;
                }

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                
                this.logger.debug(`${method} ${endpoint} -> ${response.status} (${responseTime}ms)`);
                return result;

            } catch (error) {
                this.errorCount++;
                this.logger.warn(`Request attempt ${attempt + 1} failed:`, error);

                if (attempt === this.maxRetries) {
                    throw error;
                }

                // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            }
        }
    }

    // Health and Status Methods

    /**
     * Check system health
     */
    async healthCheck(): Promise<Record<string, any>> {
        return this.makeRequest('GET', '/health');
    }

    /**
     * Get comprehensive system status
     */
    async getSystemStatus(): Promise<Record<string, any>> {
        return this.makeRequest('GET', '/status');
    }

    // Authentication Methods

    /**
     * Refresh authentication token
     */
    async refreshToken(): Promise<string> {
        const response = await this.makeRequest('POST', '/auth/refresh');
        this.accessToken = response.access_token;
        return this.accessToken!;
    }

    /**
     * Get current user profile
     */
    async getUserProfile(): Promise<Record<string, any>> {
        return this.makeRequest('GET', '/auth/profile');
    }

    // Multi-Agent Consensus Methods

    /**
     * Submit request for multi-agent consensus
     */
    async submitConsensusRequest(request: ConsensusRequest): Promise<ConsensusResult> {
        const requestData = {
            request_type: request.requestType,
            context_data: request.contextData,
            user_id: request.userId,
            resource_path: request.resourcePath,
            priority: request.priority || 5,
            timeout_seconds: request.timeoutSeconds || 30,
            required_agents: request.requiredAgents,
            metadata: request.metadata || {}
        };

        const response = await this.makeRequest('POST', '/consensus/submit', requestData);

        return {
            requestId: response.request_id,
            decision: response.decision,
            confidenceScore: response.confidence_score,
            participatingAgents: response.participating_agents,
            consensusTimeMs: response.consensus_time_ms,
            detailedVotes: response.detailed_votes,
            riskAssessment: response.risk_assessment,
            timestamp: new Date(response.timestamp),
            success: response.success
        };
    }

    /**
     * Get consensus result by request ID
     */
    async getConsensusResult(requestId: string): Promise<ConsensusResult> {
        const response = await this.makeRequest('GET', `/consensus/result/${requestId}`);

        return {
            requestId: response.request_id,
            decision: response.decision,
            confidenceScore: response.confidence_score,
            participatingAgents: response.participating_agents,
            consensusTimeMs: response.consensus_time_ms,
            detailedVotes: response.detailed_votes,
            riskAssessment: response.risk_assessment,
            timestamp: new Date(response.timestamp),
            success: response.success
        };
    }

    /**
     * List active consensus operations
     */
    async listActiveConsensus(): Promise<Record<string, any>[]> {
        const response = await this.makeRequest('GET', '/consensus/active');
        return response.active_consensus;
    }

    // Zero-Knowledge Proof Methods

    /**
     * Generate zero-knowledge proof
     */
    async generateZKProof(request: ZKProofRequest): Promise<ZKProofResult> {
        const requestData = {
            circuit_type: request.circuitType,
            inputs: request.inputs,
            public_signals: request.publicSignals,
            metadata: request.metadata || {}
        };

        const response = await this.makeRequest('POST', '/zk/generate', requestData);

        return {
            proofId: response.proof_id,
            proof: response.proof,
            publicSignals: response.public_signals,
            verificationKey: response.verification_key,
            circuitType: response.circuit_type,
            generationTimeMs: response.generation_time_ms,
            valid: response.valid,
            timestamp: new Date(response.timestamp)
        };
    }

    /**
     * Verify zero-knowledge proof
     */
    async verifyZKProof(
        proofId: string, 
        proof: Record<string, any>, 
        publicSignals: string[]
    ): Promise<boolean> {
        const requestData = {
            proof_id: proofId,
            proof: proof,
            public_signals: publicSignals
        };

        const response = await this.makeRequest('POST', '/zk/verify', requestData);
        return response.valid;
    }

    // AI/ML Enhanced Decision Methods

    /**
     * Get AI/ML enhanced decision
     */
    async getAIEnhancedDecision(
        decisionType: string,
        userData: Record<string, any>,
        contextData: Record<string, any>,
        strategy: DecisionStrategy = DecisionStrategy.BALANCED
    ): Promise<Record<string, any>> {
        const requestData = {
            decision_type: decisionType,
            user_data: userData,
            context_data: contextData,
            optimization_strategy: strategy
        };

        return this.makeRequest('POST', '/ai-ml/decisions/enhance', requestData);
    }

    /**
     * Analyze user behavioral patterns
     */
    async analyzeBehavioralPatterns(
        userId: string, 
        timeRangeHours: number = 24
    ): Promise<Record<string, any>> {
        const params = {
            user_id: userId,
            time_range_hours: timeRangeHours.toString()
        };

        return this.makeRequest('GET', '/ai-ml/analytics/patterns', undefined, params);
    }

    // Cross-Chain Methods

    /**
     * Submit cross-chain transaction
     */
    async submitCrossChainTransaction(
        sourceChain: string,
        targetChain: string,
        transactionData: Record<string, any>
    ): Promise<Record<string, any>> {
        const requestData = {
            source_chain: sourceChain,
            target_chain: targetChain,
            transaction_data: transactionData
        };

        return this.makeRequest('POST', '/crosschain/submit', requestData);
    }

    /**
     * Get cross-chain transaction status
     */
    async getCrossChainStatus(transactionId: string): Promise<Record<string, any>> {
        return this.makeRequest('GET', `/crosschain/status/${transactionId}`);
    }

    // Observability Methods

    /**
     * Record custom metric
     */
    async recordMetric(
        name: string, 
        value: number, 
        labels: Record<string, string> = {}
    ): Promise<Record<string, any>> {
        const requestData = {
            name,
            value,
            labels
        };

        return this.makeRequest('POST', '/observability/metrics/record', requestData);
    }

    /**
     * Get system dashboard data
     */
    async getSystemDashboard(): Promise<Record<string, any>> {
        return this.makeRequest('GET', '/observability/dashboard');
    }

    /**
     * Manually trigger an alert
     */
    async triggerAlert(
        metricName: string, 
        value: number, 
        description: string = 'SDK triggered alert'
    ): Promise<Record<string, any>> {
        const requestData = {
            metric_name: metricName,
            value,
            description
        };

        return this.makeRequest('POST', '/observability/alerts/trigger', requestData);
    }

    // Vault and Secret Management Methods

    /**
     * Store secret in vault
     */
    async storeSecret(
        vaultId: string,
        secretName: string,
        secretValue: string,
        metadata: Record<string, any> = {}
    ): Promise<Record<string, any>> {
        const requestData = {
            vault_id: vaultId,
            secret_name: secretName,
            secret_value: secretValue,
            metadata
        };

        return this.makeRequest('POST', '/vaults/secrets', requestData);
    }

    /**
     * Retrieve secret from vault
     */
    async retrieveSecret(vaultId: string, secretName: string): Promise<Record<string, any>> {
        const params = {
            vault_id: vaultId,
            secret_name: secretName
        };

        return this.makeRequest('GET', '/vaults/secrets', undefined, params);
    }

    // Performance and Statistics

    /**
     * Get client performance statistics
     */
    getClientStats(): ClientStats {
        const avgResponseTime = this.totalResponseTime / Math.max(this.requestCount, 1);
        const errorRate = this.errorCount / Math.max(this.requestCount, 1) * 100;

        return {
            totalRequests: this.requestCount,
            averageResponseTimeMs: avgResponseTime,
            errorCount: this.errorCount,
            errorRatePercent: errorRate,
            baseUrl: this.baseUrl,
            authenticated: !!this.accessToken
        };
    }
}

// Convenience functions for common operations

/**
 * Create and connect ReliQuary client
 */
export async function createClient(
    baseUrl: string = 'http://localhost:8000',
    apiKey?: string,
    username?: string,
    password?: string
): Promise<ReliQuaryClient> {
    const credentials: AuthCredentials = {
        apiKey,
        username,
        password
    };

    const client = new ReliQuaryClient({ baseUrl, credentials });
    await client.connect();
    return client;
}

/**
 * Quick consensus operation
 */
export async function quickConsensus(
    baseUrl: string,
    apiKey: string,
    requestType: ConsensusType,
    contextData: Record<string, any>,
    userId: string,
    resourcePath: string
): Promise<ConsensusResult> {
    const client = await createClient(baseUrl, apiKey);
    try {
        const request: ConsensusRequest = {
            requestType,
            contextData,
            userId,
            resourcePath
        };
        return await client.submitConsensusRequest(request);
    } finally {
        await client.disconnect();
    }
}

/**
 * Quick AI-enhanced decision
 */
export async function quickAIDecision(
    baseUrl: string,
    apiKey: string,
    decisionType: string,
    userData: Record<string, any>,
    contextData: Record<string, any>
): Promise<Record<string, any>> {
    const client = await createClient(baseUrl, apiKey);
    try {
        return await client.getAIEnhancedDecision(decisionType, userData, contextData);
    } finally {
        await client.disconnect();
    }
}

// Example usage
async function example() {
    const client = new ReliQuaryClient({
        baseUrl: 'http://localhost:8000',
        credentials: { apiKey: 'your-api-key' }
    });

    await client.connect();

    try {
        // Health check
        const health = await client.healthCheck();
        console.log('System health:', health);

        // Submit consensus request
        const request: ConsensusRequest = {
            requestType: ConsensusType.ACCESS_REQUEST,
            contextData: { resource_sensitivity: 'high' },
            userId: 'user123',
            resourcePath: '/secure/data'
        };

        const result = await client.submitConsensusRequest(request);
        console.log('Consensus decision:', result.decision);

        // Record metric
        await client.recordMetric('sdk_usage', 1.0, { operation: 'consensus' });

        // Get client statistics
        const stats = client.getClientStats();
        console.log('Client stats:', stats);

    } finally {
        await client.disconnect();
    }
}

export default ReliQuaryClient;