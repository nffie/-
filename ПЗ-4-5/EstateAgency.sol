// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract EstateAgency {

    struct Estate {
        address owner;
        string info;
        uint area;
        bool isSale;
        bool isBlocked;
        bool isGift;
    }

    struct Sale {
        uint estateID;
        address owner;
        address newOwner;
        uint price;
        address[] buyers;
        uint[] bids;
        uint time;
    }

    struct Gift {
        uint estateID;
        address donor;
        address recipient;
        uint time;
        bool isAccepted;
        bool isRejected;
    }

    uint public SALE_TIME = 300;
    uint public GIFT_TIME = 300;

    address public admin;

    Estate[] public estates;
    Sale[] public sales;
    Gift[] public gifts;

    constructor(address _admin) {
        admin = _admin;
    }

    modifier isAdmin() {
        require(msg.sender == admin, "Function only for admin.");
        _;
    }

    // Функции администратора контракта
    function createEstate(address _owner, string memory _info,
                          uint _area) external isAdmin returns (uint) {
        require(_owner != address(0), "Invalid owner address");
        require(_area > 0, "Area must be positive");
        estates.push(Estate(_owner, _info, _area, false, false, false));
        return estates.length - 1;
    }

    function blockEstate(uint _estateID) external isAdmin {
        require(_estateID < estates.length, "Invalid estateID");
        require(!estates[_estateID].isBlocked, "Estate already blocked");
        estates[_estateID].isBlocked = true;
    }

    function unBlockEstate(uint _estateID) external isAdmin {
        require(_estateID < estates.length, "Invalid estateID");
        require(estates[_estateID].isBlocked, "Estate is not blocked");
        estates[_estateID].isBlocked = false;
    }

    // Продажа объектов
    modifier onlyOwner(uint _estateID) {
        require(_estateID < estates.length, "Invalid estateID");
        require(msg.sender == estates[_estateID].owner, "Function only for owner");
        _;
    }

    modifier notOnSaleOrGift(uint _estateID) {
        Estate storage object = estates[_estateID];
        require(!object.isSale, "Estate already on sale");
        require(!object.isGift, "Estate already on gift");
        _;
    }

    function createSale(uint _estateID, uint _price) external onlyOwner(_estateID) notOnSaleOrGift(_estateID) {
        Estate storage object = estates[_estateID];
        require(_price > 10**6 wei, "Too low price");
        require(!object.isBlocked, "Estate is blocked");
        address[] memory _buyers;
        uint[] memory _bids;
        sales.push(Sale(_estateID, object.owner, address(0), _price, _buyers, _bids, block.timestamp));
        object.isSale = true;
    }

    function makeBid(uint _saleID) external payable {
        require(_saleID < sales.length, "Invalid saleID");
        Sale storage currSale = sales[_saleID];
        Estate storage object = estates[currSale.estateID];
        require(object.isSale, "Estate is not on sale");
        require(!object.isBlocked, "Estate is blocked");
        require(currSale.newOwner == address(0), "This sale is closed");
        require(msg.value >= currSale.price, "Bid too low");
        require(block.timestamp <= currSale.time + SALE_TIME, "Time is over");
        require(msg.sender != object.owner, "Selfselling");

        for (uint i=0; i<currSale.buyers.length; i++) {
            require(msg.sender != currSale.buyers[i], "You already made a bid");
        }
        currSale.buyers.push(msg.sender);
        currSale.bids.push(msg.value);
    }

    function getBuyers(uint _saleID) external view returns (address[] memory) {
        require(_saleID < sales.length, "Invalid saleID");
        return(sales[_saleID].buyers);
    }

    function getBids(uint _saleID) external view returns (uint[] memory) {
        require(_saleID < sales.length, "Invalid saleID");
        return(sales[_saleID].bids);
    }

    function acceptBid(uint _saleID, uint _buyerID) external onlyOwner(sales[_saleID].estateID) {
        Sale storage currSale = sales[_saleID];
        Estate storage object = estates[currSale.estateID];
        require(_buyerID < currSale.buyers.length, "Wrong buyerID");
        require(object.isSale, "Estate is not on sale");
        require(!object.isBlocked, "Estate is blocked");
        require(currSale.newOwner == address(0), "This sale is closed");
        require(block.timestamp <= currSale.time + SALE_TIME, "Time is over");
        payable(object.owner).transfer(currSale.bids[_buyerID]);
        for (uint i=0; i<currSale.buyers.length; i++) {
            if (i != _buyerID) {
                payable(currSale.buyers[i]).transfer(currSale.bids[i]);
            }
        }
        currSale.newOwner = currSale.buyers[_buyerID];
        object.owner = currSale.newOwner;
        object.isSale = false;
    }

    // ----------------------------- ✦ ДАРЕНИЕ ✦ -----------------------------
    function createGift(uint _estateID, address _recipient) external onlyOwner(_estateID) notOnSaleOrGift(_estateID) {
        Estate storage object = estates[_estateID];
        require(!object.isBlocked, "Estate is blocked");
        require(_recipient != address(0), "Invalid recipient");
        gifts.push(Gift(_estateID, msg.sender, _recipient, block.timestamp, false, false));
        object.isGift = true;
    }

    function acceptGift(uint _giftID) external {
        require(_giftID < gifts.length, "Invalid giftID");
        Gift storage g = gifts[_giftID];
        Estate storage object = estates[g.estateID];
        require(msg.sender == g.recipient, "Only recipient can accept");
        require(!g.isAccepted && !g.isRejected, "Gift already resolved");
        g.isAccepted = true;
        object.owner = g.recipient;
        object.isGift = false;
    }

    function rejectGift(uint _giftID) external {
        require(_giftID < gifts.length, "Invalid giftID");
        Gift storage g = gifts[_giftID];
        Estate storage object = estates[g.estateID];
        require(msg.sender == g.recipient, "Only recipient can reject");
        require(!g.isAccepted && !g.isRejected, "Gift already resolved");
        g.isRejected = true;
        object.isGift = false;
    }

    function cancelGift(uint _giftID) external {
        require(_giftID < gifts.length, "Invalid giftID");
        Gift storage g = gifts[_giftID];
        Estate storage object = estates[g.estateID];
        require(msg.sender == g.donor, "Only donor can cancel");
        require(!g.isAccepted && !g.isRejected, "Gift already resolved");
        g.isRejected = true;
        object.isGift = false;
    }

    function checkGiftTimeout(uint _giftID) external {
        require(_giftID < gifts.length, "Invalid giftID");
        Gift storage g = gifts[_giftID];
        Estate storage object = estates[g.estateID];
        require(!g.isAccepted && !g.isRejected, "Gift already resolved");
        if (block.timestamp > g.time + GIFT_TIME) {
            g.isRejected = true;
            object.isGift = false;
        }
    }
}
