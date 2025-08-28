// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ReliQuaryGovernance
 * @dev Smart contract for cross-chain governance and consensus coordination
 * 
 * This contract manages governance proposals, voting, and execution
 * for the ReliQuary multi-agent consensus system across multiple blockchains.
 */
contract ReliQuaryGovernance {
    
    // Governance structures
    struct Proposal {
        uint256 id;
        address proposer;
        string proposalType;
        string contentHash; // IPFS hash or similar
        uint256 votingStart;
        uint256 votingEnd;
        uint256 executionDelay;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        bool cancelled;
        mapping(address => bool) hasVoted;
        mapping(address => bool) votes;
    }
    
    struct Agent {
        address agentAddress;
        string agentType; // "neutral", "permissive", "strict", "watchdog"
        uint256 votingPower;
        bool active;
        string publicKey; // For signature verification
    }
    
    struct ConsensusDecision {
        string requestId;
        string decisionType;
        string finalDecision;
        uint256 consensusConfidence;
        string[] participatingAgents;
        uint256 timestamp;
        string proofHash;
        bool validated;
    }
    
    // State variables
    mapping(uint256 => Proposal) public proposals;
    mapping(address => Agent) public agents;
    mapping(string => ConsensusDecision) public consensusDecisions;
    
    uint256 public proposalCount;
    uint256 public constant VOTING_PERIOD = 24 hours;
    uint256 public constant EXECUTION_DELAY = 2 hours;
    uint256 public constant QUORUM_THRESHOLD = 3;
    
    address public admin;
    bool public paused;
    
    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string proposalType,
        string contentHash
    );
    
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        bool vote,
        uint256 votingPower
    );
    
    event ProposalExecuted(
        uint256 indexed proposalId,
        bool success
    );
    
    event AgentRegistered(
        address indexed agentAddress,
        string agentType,
        uint256 votingPower
    );
    
    event ConsensusRecorded(
        string indexed requestId,
        string finalDecision,
        uint256 consensusConfidence
    );
    
    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function");
        _;
    }
    
    modifier onlyActiveAgent() {
        require(agents[msg.sender].active, "Only active agents can call this function");
        _;
    }
    
    modifier notPaused() {
        require(!paused, "Contract is paused");
        _;
    }
    
    modifier proposalExists(uint256 proposalId) {
        require(proposalId <= proposalCount && proposalId > 0, "Proposal does not exist");
        _;
    }
    
    // Constructor
    constructor() {
        admin = msg.sender;
        paused = false;
    }
    
    /**
     * @dev Register a new agent in the system
     * @param agentAddress Address of the agent
     * @param agentType Type of agent (neutral, permissive, strict, watchdog)
     * @param votingPower Voting power assigned to the agent
     * @param publicKey Public key for signature verification
     */
    function registerAgent(
        address agentAddress,
        string memory agentType,
        uint256 votingPower,
        string memory publicKey
    ) external onlyAdmin notPaused {
        require(agentAddress != address(0), "Invalid agent address");
        require(votingPower > 0, "Voting power must be greater than 0");
        require(!agents[agentAddress].active, "Agent already registered");
        
        agents[agentAddress] = Agent({
            agentAddress: agentAddress,
            agentType: agentType,
            votingPower: votingPower,
            active: true,
            publicKey: publicKey
        });
        
        emit AgentRegistered(agentAddress, agentType, votingPower);
    }
    
    /**
     * @dev Create a new governance proposal
     * @param proposalType Type of proposal
     * @param contentHash Hash of the proposal content (IPFS or similar)
     */
    function createProposal(
        string memory proposalType,
        string memory contentHash
    ) external onlyActiveAgent notPaused returns (uint256) {
        proposalCount++;
        uint256 proposalId = proposalCount;
        
        Proposal storage newProposal = proposals[proposalId];
        newProposal.id = proposalId;
        newProposal.proposer = msg.sender;
        newProposal.proposalType = proposalType;
        newProposal.contentHash = contentHash;
        newProposal.votingStart = block.timestamp;
        newProposal.votingEnd = block.timestamp + VOTING_PERIOD;
        newProposal.executionDelay = EXECUTION_DELAY;
        newProposal.yesVotes = 0;
        newProposal.noVotes = 0;
        newProposal.executed = false;
        newProposal.cancelled = false;
        
        emit ProposalCreated(proposalId, msg.sender, proposalType, contentHash);
        return proposalId;
    }
    
    /**
     * @dev Vote on a proposal
     * @param proposalId ID of the proposal
     * @param vote True for yes, false for no
     */
    function voteOnProposal(
        uint256 proposalId,
        bool vote
    ) external onlyActiveAgent notPaused proposalExists(proposalId) {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp >= proposal.votingStart, "Voting has not started");
        require(block.timestamp <= proposal.votingEnd, "Voting has ended");
        require(!proposal.hasVoted[msg.sender], "Agent has already voted");
        require(!proposal.executed && !proposal.cancelled, "Proposal is finalized");
        
        Agent memory agent = agents[msg.sender];
        
        proposal.hasVoted[msg.sender] = true;
        proposal.votes[msg.sender] = vote;
        
        if (vote) {
            proposal.yesVotes += agent.votingPower;
        } else {
            proposal.noVotes += agent.votingPower;
        }
        
        emit VoteCast(proposalId, msg.sender, vote, agent.votingPower);
    }
    
    /**
     * @dev Execute a passed proposal
     * @param proposalId ID of the proposal
     */
    function executeProposal(
        uint256 proposalId
    ) external proposalExists(proposalId) notPaused {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp > proposal.votingEnd, "Voting period not ended");
        require(block.timestamp >= proposal.votingEnd + proposal.executionDelay, "Execution delay not met");
        require(!proposal.executed, "Proposal already executed");
        require(!proposal.cancelled, "Proposal was cancelled");
        
        // Check if proposal passed
        uint256 totalVotes = proposal.yesVotes + proposal.noVotes;
        require(totalVotes >= QUORUM_THRESHOLD, "Quorum not met");
        require(proposal.yesVotes > proposal.noVotes, "Proposal did not pass");
        
        proposal.executed = true;
        
        // Execute proposal logic based on type
        bool success = _executeProposalLogic(proposal);
        
        emit ProposalExecuted(proposalId, success);
    }
    
    /**
     * @dev Record a consensus decision from the multi-agent system
     * @param requestId Unique identifier for the consensus request
     * @param decisionType Type of decision made
     * @param finalDecision The final consensus decision
     * @param consensusConfidence Confidence level of the consensus
     * @param participatingAgents Array of participating agent identifiers
     * @param proofHash Hash of the consensus proof
     */
    function recordConsensusDecision(
        string memory requestId,
        string memory decisionType,
        string memory finalDecision,
        uint256 consensusConfidence,
        string[] memory participatingAgents,
        string memory proofHash
    ) external onlyActiveAgent notPaused {
        require(bytes(requestId).length > 0, "Request ID cannot be empty");
        require(!consensusDecisions[requestId].validated, "Decision already recorded");
        
        consensusDecisions[requestId] = ConsensusDecision({
            requestId: requestId,
            decisionType: decisionType,
            finalDecision: finalDecision,
            consensusConfidence: consensusConfidence,
            participatingAgents: participatingAgents,
            timestamp: block.timestamp,
            proofHash: proofHash,
            validated: true
        });
        
        emit ConsensusRecorded(requestId, finalDecision, consensusConfidence);
    }
    
    /**
     * @dev Verify a consensus decision
     * @param requestId The request ID to verify
     * @return isValid Whether the consensus decision is valid
     * @return decision The consensus decision
     * @return confidence The confidence level
     */
    function verifyConsensusDecision(
        string memory requestId
    ) external view returns (bool isValid, string memory decision, uint256 confidence) {
        ConsensusDecision memory consensusDecision = consensusDecisions[requestId];
        
        return (
            consensusDecision.validated,
            consensusDecision.finalDecision,
            consensusDecision.consensusConfidence
        );
    }
    
    /**
     * @dev Get proposal details
     * @param proposalId ID of the proposal
     */
    function getProposal(
        uint256 proposalId
    ) external view proposalExists(proposalId) returns (
        address proposer,
        string memory proposalType,
        string memory contentHash,
        uint256 votingStart,
        uint256 votingEnd,
        uint256 yesVotes,
        uint256 noVotes,
        bool executed,
        bool cancelled
    ) {
        Proposal storage proposal = proposals[proposalId];
        
        return (
            proposal.proposer,
            proposal.proposalType,
            proposal.contentHash,
            proposal.votingStart,
            proposal.votingEnd,
            proposal.yesVotes,
            proposal.noVotes,
            proposal.executed,
            proposal.cancelled
        );
    }
    
    /**
     * @dev Get agent information
     * @param agentAddress Address of the agent
     */
    function getAgent(
        address agentAddress
    ) external view returns (
        string memory agentType,
        uint256 votingPower,
        bool active,
        string memory publicKey
    ) {
        Agent memory agent = agents[agentAddress];
        
        return (
            agent.agentType,
            agent.votingPower,
            agent.active,
            agent.publicKey
        );
    }
    
    /**
     * @dev Check if an address has voted on a proposal
     * @param proposalId ID of the proposal
     * @param voter Address of the voter
     */
    function hasVoted(
        uint256 proposalId,
        address voter
    ) external view proposalExists(proposalId) returns (bool) {
        return proposals[proposalId].hasVoted[voter];
    }
    
    /**
     * @dev Get vote of an address on a proposal
     * @param proposalId ID of the proposal
     * @param voter Address of the voter
     */
    function getVote(
        uint256 proposalId,
        address voter
    ) external view proposalExists(proposalId) returns (bool) {
        require(proposals[proposalId].hasVoted[voter], "Address has not voted");
        return proposals[proposalId].votes[voter];
    }
    
    /**
     * @dev Emergency pause function
     */
    function pause() external onlyAdmin {
        paused = true;
    }
    
    /**
     * @dev Unpause function
     */
    function unpause() external onlyAdmin {
        paused = false;
    }
    
    /**
     * @dev Deactivate an agent
     * @param agentAddress Address of the agent to deactivate
     */
    function deactivateAgent(address agentAddress) external onlyAdmin {
        require(agents[agentAddress].active, "Agent is not active");
        agents[agentAddress].active = false;
    }
    
    /**
     * @dev Internal function to execute proposal logic
     * @param proposal The proposal to execute
     */
    function _executeProposalLogic(
        Proposal storage proposal
    ) internal returns (bool) {
        // Implementation depends on proposal type
        // This is a simplified version
        
        if (keccak256(bytes(proposal.proposalType)) == keccak256(bytes("SYSTEM_UPGRADE"))) {
            // Handle system upgrade
            return true;
        } else if (keccak256(bytes(proposal.proposalType)) == keccak256(bytes("TRUST_UPDATE"))) {
            // Handle trust parameter update
            return true;
        } else if (keccak256(bytes(proposal.proposalType)) == keccak256(bytes("EMERGENCY_OVERRIDE"))) {
            // Handle emergency override
            return true;
        }
        
        return false;
    }
    
    /**
     * @dev Get current governance statistics
     */
    function getGovernanceStats() external view returns (
        uint256 totalProposals,
        uint256 activeAgents,
        uint256 totalDecisions,
        bool contractPaused
    ) {
        uint256 activeAgentCount = 0;
        uint256 totalDecisionCount = 0;
        
        // Count active agents (simplified - in production use a more efficient method)
        // This is just for demonstration
        
        return (
            proposalCount,
            activeAgentCount,
            totalDecisionCount,
            paused
        );
    }
}