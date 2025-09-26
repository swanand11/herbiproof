// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CropToken {
    
    struct Crop {
        uint256 id;
        string metadata;
        address owner;
    }

    mapping(uint256 => Crop) public crops;
    uint256 public nextId;

    mapping(address => bool) public registeredUsers;

    event CropCreated(uint256 id, string metadata, address owner);
    event CropTransferred(uint256 id, address from, address to);
    event UserRegistered(address user);

    function registerUser() external {
        require(!registeredUsers[msg.sender], "User already registered");
        registeredUsers[msg.sender] = true;
        emit UserRegistered(msg.sender);
    }

    modifier onlyRegistered() {
        require(registeredUsers[msg.sender], "User not registered");
        _;
    }

    function createCrop(string memory _metadata) external onlyRegistered {
        uint256 cropId = nextId;
        crops[cropId] = Crop({ id: cropId, metadata: _metadata, owner: msg.sender });
        emit CropCreated(cropId, _metadata, msg.sender);
        nextId++;
    }

    function authenticate(uint256 _id, address _owner) external view onlyRegistered returns (bool) {
        Crop memory c = crops[_id];
        return (c.owner == _owner);
    }

    function transferCrop(uint256 _id, address _to) external onlyRegistered {
        Crop storage c = crops[_id];
        require(c.owner == msg.sender, "Only the owner can transfer this token");
        require(_to != address(0), "Cannot transfer to zero address");
        require(registeredUsers[_to], "Recipient must be registered");

        address previousOwner = c.owner;
        c.owner = _to;
        emit CropTransferred(_id, previousOwner, _to);
    }

    function getCrop(uint256 _id) external view returns (uint256, string memory, address) {
        Crop memory c = crops[_id];
        return (c.id, c.metadata, c.owner);
    }
}
