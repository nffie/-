// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract BallotCPP {

    struct Voter {
        bool registered;
        bool voted;
        uint[3] weights;
    }

    struct Proposal {
        string name;
        uint totalConfidence;
        uint supporters;
    }

    Proposal[3] public proposals;
    mapping(address => Voter) public voters;

    uint public registeredVoters;
    uint public votingEnd;
    address public owner;

    constructor(
        string[3] memory proposalNames,
        uint votingDurationSeconds
    ) {
        owner = msg.sender;
        votingEnd = block.timestamp + votingDurationSeconds;

        for (uint i = 0; i < 3; i++) {
            proposals[i].name = proposalNames[i];
        }
    }

    function registerVoter(address voter) external {
        require(msg.sender == owner, "Only owner");
        require(!voters[voter].registered, "Already registered");

        voters[voter].registered = true;
        registeredVoters++;
    }

    function vote(uint[3] memory weights) external {
        require(block.timestamp <= votingEnd, "Voting finished");
        require(voters[msg.sender].registered, "Not registered");
        require(!voters[msg.sender].voted, "Already voted");

        uint sum;
        for (uint i = 0; i < 3; i++) {
            sum += weights[i];
        }
        require(sum == 100, "Sum must be 100");

        voters[msg.sender].voted = true;
        voters[msg.sender].weights = weights;

        for (uint i = 0; i < 3; i++) {
            if (weights[i] > 0) {
                proposals[i].totalConfidence += weights[i];
                proposals[i].supporters++;
            }
        }
    }

    function winningProposal() external view returns (uint) {
        require(block.timestamp > votingEnd, "Voting not ended");

        uint maxConfidence = 0;
        uint winner = 999;
        bool conflict = false;

        for (uint i = 0; i < 3; i++) {
            if (proposals[i].supporters * 2 <= registeredVoters) {
                continue;
            }

            if (proposals[i].totalConfidence > maxConfidence) {
                maxConfidence = proposals[i].totalConfidence;
                winner = i;
                conflict = false;
            } else if (
                proposals[i].totalConfidence == maxConfidence &&
                maxConfidence != 0
            ) {
                conflict = true;
            }
        }

        if (winner == 999 || conflict) {
            return 999;
        }

        return winner;
    }

    function voterDetails(address voter)
        external
        view
        returns (uint[3] memory)
    {
        return voters[voter].weights;
    }
}
