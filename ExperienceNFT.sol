// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ExperienceNFT is ERC721URIStorage, Ownable {
    uint256 public tokenCounter;

    constructor() ERC721("ExperienceNFT", "EXNFT") Ownable(msg.sender) {
    tokenCounter = 0;
    }

    function issueCertificate(address recipient, string memory tokenURI) public onlyOwner returns (uint256) {
        uint256 newItemId = tokenCounter;
        _safeMint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);
        tokenCounter += 1;
        return newItemId;
    }
}
