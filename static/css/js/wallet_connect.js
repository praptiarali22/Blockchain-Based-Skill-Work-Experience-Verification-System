async function getWalletAddress() {
    if (typeof window.ethereum !== 'undefined') {
        const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
        return accounts[0];
    } else {
        alert("Please install MetaMask!");
        throw new Error("MetaMask not available");
    }
}
