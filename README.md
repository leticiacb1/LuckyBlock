## 🍀 LuckyBlock
### A Lottery on the Blockchain

#### 🔍 Description

It is a decentralized lottery platform built on blockchain technology, designed to eliminate the main flaws of traditional lotteries—such as lack of transparency, vulnerability to fraud, loss of physical tickets, and delays in prize distribution.

##### How the system would work

<img src="media/Diagram.png" width="400"/>

###### 1. Start of the Lottery

An administrator (the contract owner) initializes a new lottery round via a Smart Contract.

###### 2. Ticket Purchase

Users access a web interface, choose their numbers, and purchase a ticket.

The bet is recorded on the blockchain by the smart contract, saving the player's wallet address and the selected numbers.

###### 3. Closing of Bets

After the deadline, the contract automatically blocks any new bets.

###### 4. Drawing (via Oracle)

The drawing takes place off-chain, using traditional methods.

An oracle then sends the drawn numbers to the smart contract on the blockchain.

###### 5. Winner Verification

The smart contract compares all bets with the drawn numbers.

It identifies the users who matched the numbers and automatically calculates the prize amounts.

###### 6. Prize Distribution

Winners can claim their prizes within a defined period after the drawing results are announced.


#### ⚙️ Configuration


#### 📌 How to run

##### 1. Constract

##### 2. Tests