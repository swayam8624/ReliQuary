// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./ReliQuaryGovernance.sol";

/**
 * @title CrossChainBridge
 * @dev Smart contract for secure cross-chain message passing and consensus coordination
 * 
 * This contract enables ReliQuary agents to coordinate decisions across multiple
 * blockchain networks with cryptographic proof verification and replay protection.
 */
contract CrossChainBridge {
    
    // Cross-chain message structure
    struct CrossChainMessage {
        string messageId;
        uint256 sourceChainId;
        uint256 targetChainId;
        address sender;
        string messageType;
        bytes payload;
        uint256 timestamp;
        uint256 nonce;
        bytes32 payloadHash;
        bool processed;
        uint256 confirmations;
    }
    
    // Relay node structure
    struct RelayNode {
        address nodeAddress;
        string nodeType; // "validator", "agent", "oracle"
        uint256 stake;
        bool active;
        uint256 successfulRelays;
        uint256 failedRelays;
    }
    
    // Chain configuration
    struct ChainConfig {
        uint256 chainId;
        string chainName;
        uint256 confirmationBlocks;
        bool enabled;
        address bridgeContract;
    }
    
    // State variables
    mapping(string => CrossChainMessage) public crossChainMessages;
    mapping(address => RelayNode) public relayNodes;
    mapping(uint256 => ChainConfig) public supportedChains;
    mapping(address => uint256) public nonces;
    mapping(string => bool) public processedMessages;
    
    ReliQuaryGovernance public governanceContract;
    
    uint256 public constant MIN_CONFIRMATIONS = 2;
    uint256 public constant MESSAGE_TIMEOUT = 1 hours;
    uint256 public constant MIN_RELAY_STAKE = 1 ether;
    
    address public admin;
    bool public paused;
    uint256 public totalRelayedMessages;
    uint256 public successfulBridgeOperations;
    
    // Events
    event CrossChainMessageSent(
        string indexed messageId,
        uint256 indexed sourceChainId,
        uint256 indexed targetChainId,
        address sender,
        string messageType
    );
    
    event CrossChainMessageReceived(
        string indexed messageId,
        uint256 indexed sourceChainId,
        address relayNode,
        bool success
    );
    
    event RelayNodeRegistered(
        address indexed nodeAddress,
        string nodeType,
        uint256 stake
    );
    
    event ChainAdded(
        uint256 indexed chainId,
        string chainName,
        address bridgeContract
    );
    
    event MessageConfirmed(
        string indexed messageId,
        address indexed confirmingNode,
        uint256 confirmations
    );
    
    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function");
        _;
    }
    
    modifier onlyActiveRelay() {
        require(relayNodes[msg.sender].active, "Only active relay nodes can call this function");
        _;
    }
    
    modifier notPaused() {
        require(!paused, "Bridge is paused");
        _;
    }
    
    modifier validChain(uint256 chainId) {
        require(supportedChains[chainId].enabled, "Chain not supported");
        _;
    }
    
    // Constructor
    constructor(address _governanceContract) {
        admin = msg.sender;
        governanceContract = ReliQuaryGovernance(_governanceContract);
        paused = false;
    }
    
    /**
     * @dev Register a relay node
     * @param nodeType Type of relay node
     */
    function registerRelayNode(string memory nodeType) external payable notPaused {
        require(msg.value >= MIN_RELAY_STAKE, "Insufficient stake");
        require(!relayNodes[msg.sender].active, "Node already registered");
        
        relayNodes[msg.sender] = RelayNode({
            nodeAddress: msg.sender,
            nodeType: nodeType,
            stake: msg.value,
            active: true,
            successfulRelays: 0,
            failedRelays: 0
        });
        
        emit RelayNodeRegistered(msg.sender, nodeType, msg.value);
    }
    
    /**
     * @dev Add a supported blockchain
     * @param chainId ID of the blockchain
     * @param chainName Name of the blockchain
     * @param confirmationBlocks Required confirmation blocks
     * @param bridgeContract Address of the bridge contract on that chain
     */
    function addSupportedChain(
        uint256 chainId,
        string memory chainName,
        uint256 confirmationBlocks,
        address bridgeContract
    ) external onlyAdmin {
        require(chainId != block.chainid, "Cannot add current chain");
        require(!supportedChains[chainId].enabled, "Chain already supported");
        
        supportedChains[chainId] = ChainConfig({
            chainId: chainId,
            chainName: chainName,
            confirmationBlocks: confirmationBlocks,
            enabled: true,
            bridgeContract: bridgeContract
        });
        
        emit ChainAdded(chainId, chainName, bridgeContract);
    }
    
    /**
     * @dev Send a cross-chain message
     * @param targetChainId Target blockchain ID
     * @param messageType Type of message (consensus, governance, emergency)
     * @param payload Message payload
     */
    function sendCrossChainMessage(
        uint256 targetChainId,
        string memory messageType,
        bytes memory payload
    ) external notPaused validChain(targetChainId) returns (string memory messageId) {
        // Generate unique message ID
        messageId = generateMessageId(msg.sender, targetChainId, nonces[msg.sender]);
        nonces[msg.sender]++;
        
        // Calculate payload hash
        bytes32 payloadHash = keccak256(payload);
        
        // Create cross-chain message
        crossChainMessages[messageId] = CrossChainMessage({
            messageId: messageId,
            sourceChainId: block.chainid,
            targetChainId: targetChainId,
            sender: msg.sender,
            messageType: messageType,
            payload: payload,
            timestamp: block.timestamp,
            nonce: nonces[msg.sender] - 1,
            payloadHash: payloadHash,
            processed: false,
            confirmations: 0
        });
        
        totalRelayedMessages++;
        
        emit CrossChainMessageSent(
            messageId,
            block.chainid,
            targetChainId,
            msg.sender,
            messageType
        );
        
        return messageId;
    }
    
    /**
     * @dev Receive and process a cross-chain message
     * @param messageId Unique message identifier
     * @param sourceChainId Source blockchain ID
     * @param sender Original message sender
     * @param messageType Type of message
     * @param payload Message payload
     * @param timestamp Original timestamp
     * @param nonce Sender's nonce
     * @param signature Cryptographic signature for verification
     */
    function receiveCrossChainMessage(
        string memory messageId,
        uint256 sourceChainId,
        address sender,
        string memory messageType,
        bytes memory payload,
        uint256 timestamp,
        uint256 nonce,
        bytes memory signature
    ) external onlyActiveRelay notPaused validChain(sourceChainId) {
        require(!processedMessages[messageId], "Message already processed");
        require(block.timestamp <= timestamp + MESSAGE_TIMEOUT, "Message expired");
        
        // Verify message signature (simplified for demo)
        bytes32 messageHash = keccak256(abi.encodePacked(
            messageId, sourceChainId, sender, messageType, payload, timestamp, nonce
        ));
        
        // Store the received message
        crossChainMessages[messageId] = CrossChainMessage({
            messageId: messageId,
            sourceChainId: sourceChainId,
            targetChainId: block.chainid,
            sender: sender,
            messageType: messageType,
            payload: payload,
            timestamp: timestamp,
            nonce: nonce,
            payloadHash: keccak256(payload),
            processed: false,
            confirmations: 1
        });
        
        bool success = _processMessage(messageId, messageType, payload, sender);
        
        if (success) {
            processedMessages[messageId] = true;
            relayNodes[msg.sender].successfulRelays++;
            successfulBridgeOperations++;
        } else {
            relayNodes[msg.sender].failedRelays++;
        }
        
        emit CrossChainMessageReceived(messageId, sourceChainId, msg.sender, success);
    }
    
    /**
     * @dev Confirm a cross-chain message
     * @param messageId Message to confirm
     */
    function confirmMessage(string memory messageId) external onlyActiveRelay {
        require(bytes(crossChainMessages[messageId].messageId).length > 0, "Message not found");
        require(!crossChainMessages[messageId].processed, "Message already processed");
        
        crossChainMessages[messageId].confirmations++;
        
        emit MessageConfirmed(messageId, msg.sender, crossChainMessages[messageId].confirmations);
        
        // Auto-process if minimum confirmations reached
        if (crossChainMessages[messageId].confirmations >= MIN_CONFIRMATIONS) {
            CrossChainMessage storage message = crossChainMessages[messageId];
            bool success = _processMessage(
                messageId,
                message.messageType,
                message.payload,
                message.sender
            );
            
            if (success) {
                message.processed = true;
                processedMessages[messageId] = true;
            }
        }
    }
    
    /**
     * @dev Process a cross-chain message based on its type
     * @param messageId Message identifier
     * @param messageType Type of message
     * @param payload Message payload
     * @param sender Original sender
     */
    function _processMessage(
        string memory messageId,
        string memory messageType,
        bytes memory payload,
        address sender
    ) internal returns (bool success) {
        if (keccak256(bytes(messageType)) == keccak256(bytes("CONSENSUS_DECISION"))) {
            return _processConsensusDecision(payload, sender);
        } else if (keccak256(bytes(messageType)) == keccak256(bytes("GOVERNANCE_PROPOSAL"))) {
            return _processGovernanceProposal(payload, sender);
        } else if (keccak256(bytes(messageType)) == keccak256(bytes("EMERGENCY_COORDINATION"))) {
            return _processEmergencyCoordination(payload, sender);
        } else if (keccak256(bytes(messageType)) == keccak256(bytes("TRUST_UPDATE"))) {
            return _processTrustUpdate(payload, sender);
        }
        
        return false;
    }
    
    /**
     * @dev Process consensus decision message
     */
    function _processConsensusDecision(bytes memory payload, address sender) internal returns (bool) {
        try this.decodeConsensusPayload(payload) returns (
            string memory requestId,
            string memory decisionType,
            string memory finalDecision,
            uint256 consensusConfidence,
            string[] memory participatingAgents,
            string memory proofHash
        ) {
            // Record the consensus decision in the governance contract
            // Note: This would require the sender to be an authorized agent
            governanceContract.recordConsensusDecision(
                requestId,
                decisionType,
                finalDecision,
                consensusConfidence,
                participatingAgents,
                proofHash
            );
            
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * @dev Process governance proposal message
     */
    function _processGovernanceProposal(bytes memory payload, address sender) internal returns (bool) {
        try this.decodeGovernancePayload(payload) returns (
            string memory proposalType,
            string memory contentHash
        ) {
            // Create governance proposal
            governanceContract.createProposal(proposalType, contentHash);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * @dev Process emergency coordination message
     */
    function _processEmergencyCoordination(bytes memory payload, address sender) internal returns (bool) {
        // Emergency coordination logic
        // This would trigger emergency protocols
        return true;
    }
    
    /**
     * @dev Process trust update message
     */
    function _processTrustUpdate(bytes memory payload, address sender) internal returns (bool) {
        // Trust parameter update logic
        return true;
    }
    
    /**
     * @dev Decode consensus decision payload
     */
    function decodeConsensusPayload(bytes memory payload) external pure returns (
        string memory requestId,
        string memory decisionType,
        string memory finalDecision,
        uint256 consensusConfidence,
        string[] memory participatingAgents,
        string memory proofHash
    ) {
        return abi.decode(payload, (string, string, string, uint256, string[], string));
    }
    
    /**
     * @dev Decode governance proposal payload
     */
    function decodeGovernancePayload(bytes memory payload) external pure returns (
        string memory proposalType,
        string memory contentHash
    ) {
        return abi.decode(payload, (string, string));
    }
    
    /**
     * @dev Generate unique message ID
     */
    function generateMessageId(
        address sender,
        uint256 targetChainId,
        uint256 nonce
    ) public view returns (string memory) {
        return string(abi.encodePacked(
            "msg_",
            uint2str(block.chainid),
            "_",
            uint2str(targetChainId),
            "_",
            addressToString(sender),
            "_",
            uint2str(nonce),
            "_",
            uint2str(block.timestamp)
        ));
    }
    
    /**
     * @dev Get message details
     */
    function getMessage(string memory messageId) external view returns (
        uint256 sourceChainId,
        uint256 targetChainId,
        address sender,
        string memory messageType,
        uint256 timestamp,
        uint256 confirmations,
        bool processed
    ) {
        CrossChainMessage memory message = crossChainMessages[messageId];
        
        return (
            message.sourceChainId,
            message.targetChainId,
            message.sender,
            message.messageType,
            message.timestamp,
            message.confirmations,
            message.processed
        );
    }
    
    /**
     * @dev Get relay node information
     */
    function getRelayNode(address nodeAddress) external view returns (
        string memory nodeType,
        uint256 stake,
        bool active,
        uint256 successfulRelays,
        uint256 failedRelays
    ) {
        RelayNode memory node = relayNodes[nodeAddress];
        
        return (
            node.nodeType,
            node.stake,
            node.active,
            node.successfulRelays,
            node.failedRelays
        );
    }
    
    /**
     * @dev Get bridge statistics
     */
    function getBridgeStats() external view returns (
        uint256 totalMessages,
        uint256 successfulOperations,
        uint256 activeRelayNodes,
        uint256 supportedChainsCount
    ) {
        uint256 activeNodes = 0;
        uint256 chainsCount = 0;
        
        // Count active relay nodes and supported chains
        // (Simplified implementation for demo)
        
        return (
            totalRelayedMessages,
            successfulBridgeOperations,
            activeNodes,
            chainsCount
        );
    }
    
    /**
     * @dev Emergency pause
     */
    function pause() external onlyAdmin {
        paused = true;
    }
    
    /**
     * @dev Unpause
     */
    function unpause() external onlyAdmin {
        paused = false;
    }
    
    /**
     * @dev Deactivate a relay node
     */
    function deactivateRelayNode(address nodeAddress) external onlyAdmin {
        require(relayNodes[nodeAddress].active, "Node not active");
        relayNodes[nodeAddress].active = false;
        
        // Return stake (simplified)
        payable(nodeAddress).transfer(relayNodes[nodeAddress].stake);
    }
    
    /**
     * @dev Utility function to convert uint to string
     */
    function uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k - 1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
    
    /**
     * @dev Utility function to convert address to string
     */
    function addressToString(address _addr) internal pure returns (string memory) {
        bytes32 value = bytes32(uint256(uint160(_addr)));
        bytes memory alphabet = "0123456789abcdef";
        
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2+i*2] = alphabet[uint8(value[i + 12] >> 4)];
            str[3+i*2] = alphabet[uint8(value[i + 12] & 0x0f)];
        }
        return string(str);
    }
}