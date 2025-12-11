// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract ConfidenceVoting {

    struct Proposal {
        string name;
        uint256 totalConfidence;
        uint256 votersWhoChoseIt;
    }

    struct Voter {
        bool canVote;
        bool alreadyVoted;
        uint256[3] weights;
    }

    address public chairperson;
    uint256 public votingEndTime;

    Proposal[3] public proposals;
    mapping(address => Voter) public voters;
    uint256 public totalVoters;

    constructor(string[3] memory proposalNames, uint256 votingDurationSeconds) {
        require(votingDurationSeconds > 0, "Voting duration must be more than 0 seconds");

        chairperson = msg.sender;
        votingEndTime = block.timestamp + votingDurationSeconds;

        proposals[0].name = proposalNames[0];
        proposals[1].name = proposalNames[1];
        proposals[2].name = proposalNames[2];
    }

    function registerVoter(address voterAddress) external {
        require(msg.sender == chairperson, "Only chairperson can register voters");
        require(!voters[voterAddress].canVote, "This person is already registered");

        voters[voterAddress].canVote = true;
        totalVoters++;
    }

    function vote(uint256 weight0, uint256 weight1, uint256 weight2) external {
        require(block.timestamp < votingEndTime, "Voting has ended");
        require(voters[msg.sender].canVote, "You are not registered to vote");
        require(!voters[msg.sender].alreadyVoted, "You have already voted");

        uint256 total = weight0 + weight1 + weight2;
        require(total == 100, "Weights must add up to exactly 100");

        voters[msg.sender].alreadyVoted = true;
        voters[msg.sender].weights[0] = weight0;
        voters[msg.sender].weights[1] = weight1;
        voters[msg.sender].weights[2] = weight2;

        if (weight0 > 0) {
            proposals[0].totalConfidence += weight0;
            proposals[0].votersWhoChoseIt++;
        }
        if (weight1 > 0) {
            proposals[1].totalConfidence += weight1;
            proposals[1].votersWhoChoseIt++;
        }
        if (weight2 > 0) {
            proposals[2].totalConfidence += weight2;
            proposals[2].votersWhoChoseIt++;
        }
    }

    function getWinner() external view returns (uint256) {
        require(block.timestamp >= votingEndTime, "Voting is still open");

        uint256 maxConfidence = 0;
        uint256 winnerIndex = 999;
        uint256 proposalsWithMaxConfidence = 0;

        for (uint256 i = 0; i < 3; i++) {
            if (proposals[i].totalConfidence > maxConfidence) {
                maxConfidence = proposals[i].totalConfidence;
                winnerIndex = i;
                proposalsWithMaxConfidence = 1;
            } else if (proposals[i].totalConfidence == maxConfidence && maxConfidence > 0) {
                proposalsWithMaxConfidence++;
            }
        }

        if (proposalsWithMaxConfidence > 1) {
            return 999;
        }

        if (maxConfidence == 0) {
            return 999;
        }

        uint256 halfOfVoters = totalVoters / 2;
        if (proposals[winnerIndex].votersWhoChoseIt > halfOfVoters) {
            return winnerIndex;
        }

        return 999;
    }

    function getVoterWeights(address voterAddress) external view returns (uint256[3] memory) {
        require(voters[voterAddress].canVote, "This person is not registered");
        return voters[voterAddress].weights;
    }

    function getProposalInfo(uint256 proposalId)
        external
        view
        returns (string memory name, uint256 totalConfidence, uint256 votersWhoChoseIt)
    {
        require(proposalId < 3, "Proposal must be 0, 1, or 2");
        return (
            proposals[proposalId].name,
            proposals[proposalId].totalConfidence,
            proposals[proposalId].votersWhoChoseIt
        );
    }

    function isVotingOpen() external view returns (bool) {
        return block.timestamp < votingEndTime;
    }

    function secondsUntilVotingEnds() external view returns (uint256) {
        if (block.timestamp >= votingEndTime) {
            return 0;
        }
        return votingEndTime - block.timestamp;
    }

    function getTotalVoters() external view returns (uint256) {
        return totalVoters;
    }

    function getVotesNeededForMajority() external view returns (uint256) {
        return (totalVoters / 2) + 1;
    }

}
