import base64
import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from Block import Block


class Blockchain:
    # Basic blockchain init
    # Includes the chain as a list of blocks in order, pending transactions, and known accounts
    # Includes the current value of the hash target. It can be changed at any point to vary the difficulty
    # Also initiates a genesis block
    def __init__(self, hash_target):
        self._chain = []
        self._pending_transactions = []
        self._chain.append(self.__create_genesis_block())
        self._hash_target = hash_target
        self._accounts = {}

    def __str__(self):
        return f"Chain:\n{self._chain}\n\nPending Transactions: {self._pending_transactions}\n"

    @property
    def hash_target(self):
        return self._hash_target

    @hash_target.setter
    def hash_target(self, hash_target):
        self._hash_target = hash_target

    # Creating the genesis block, taking arbitrary previous block hash since there is no previous block
    # Using the famous bitcoin genesis block string here :)  
    def __create_genesis_block(self):
        genesis_block = Block(0, [], 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
                              None, 'Genesis block using same string as bitcoin!')
        return genesis_block

    def __validate_transaction(self, transaction):
        # Digitally verify the signature against hash of the message to validate authenticity
        # Return False otherwise

        public_pem = self._accounts[transaction['message']['sender']].public_key
        public_key = serialization.load_pem_public_key(public_pem)

        b64_signature = transaction['signature']
        base64_bytes = b64_signature.encode('utf-8')
        signature = base64.b64decode(base64_bytes)

        formatted_txn_msg = json.dumps(transaction['message'], sort_keys=True)
        hashed_msg = hashlib.sha256(formatted_txn_msg.encode('utf-8')).hexdigest()
        hashed_msg_bytes = bytes(hashed_msg, 'utf-8')

        try:
            public_key.verify(
                signature,
                hashed_msg_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256())
        except InvalidSignature:
            return False

        return True

    def __process_transactions(self, transactions):
        # Appropriately transfer value from the sender to the receiver
        # For all transactions, first check that the sender has enough balance. 
        # Return False otherwise
        tmp_dict = dict.fromkeys(self._accounts)
        for key in self._accounts.keys():
            bal = self._accounts[key].balance
            tmp_dict[key] = int(bal)

        if self.negative_bal_check(transactions, tmp_dict):
            print("\n !!!!! Blockchain.py (process_transactions_fn): Unable to Create a Block and Process "
                  "transactions due to "
                  "insufficient balance -- %s -- \n" % (tmp_dict.items()))
            return False

        for txn in transactions:
            sender = txn['message']['sender']
            amount = txn['message']['value']
            receiver = txn['message']['receiver']

            if amount <= self._accounts[sender].balance:
                self._accounts[sender].decrease_balance(amount)
                self._accounts[receiver].increase_balance(amount)
            else:
                return False

        return True

    # Creates a new block and appends to the chain
    # Also clears the pending transactions as they are part of the new block now
    def create_new_block(self):
        new_block = Block(len(self._chain), self._pending_transactions, self._chain[-1].block_hash, self._hash_target)
        if self.__process_transactions(self._pending_transactions):
            self._chain.append(new_block)
            self._pending_transactions = []
            return new_block
        else:
            return False

    # Simple transaction with just one sender, one receiver, and one value
    # Created by the account and sent to the blockchain instance
    def add_transaction(self, transaction):
        if self.__validate_transaction(transaction):
            self._pending_transactions.append(transaction)
            return True
        else:
            print(f'ERROR: Transaction: {transaction} failed signature validation')
            return False

    def __validate_chain_hash_integrity(self):
        # Run through the whole blockchain and ensure that previous hash is actually the hash of the previous block
        # Return False otherwise
        # print('the chain is %s' % self._chain)
        for index in range(1, len(self._chain)):
            if self._chain[index].previous_block_hash != self._chain[index - 1].hash_block():
                print(f'Previous block hash mismatch in block index: {index}')
                return False
        return True

    def __validate_block_hash_target(self):
        # Run through the whole blockchain and ensure that block hash meets hash target criteria, and is the actual
        # hash of the block Return False otherwise
        for index in range(1, len(self._chain)):
            if int(self._chain[index].hash_block(), 16) >= int(self._chain[index].hash_target, 16):
                print(f'Hash target not achieved in block index: {index}')
                return False
        return True

    def __validate_complete_account_balances(self):
        # Run through the whole blockchain and ensure that balances never become negative from any transaction
        # Return False otherwise

        tmp_dict = dict.fromkeys(self._accounts)
        for key in self._accounts.keys():
            init_bal = self._accounts[key].initial_balance
            tmp_dict[key] = int(init_bal)

        for index in range(0, len(self._chain)):
            curr_chain_txn = self._chain[index].transactions

            if self.negative_bal_check(curr_chain_txn, tmp_dict):
                print(
                    "\n !!! Blokchain.py (validate_complete_account_balances): One of the account balance turned "
                    "negative "
                    "on reconciliation -- %s --\n" % (
                        tmp_dict.items()))
                return False
        return True

    # Blockchain validation function
    # Runs through the whole blockchain and applies appropriate validations
    def validate_blockchain(self):
        # Call __validate_chain_hash_integrity and implement that method. Return False if check fails
        # Call __validate_block_hash_target and implement that method. Return False if check fails
        # Call __validate_complete_account_balances and implement that method. Return False if check fails
        if not self.__validate_chain_hash_integrity():
            return False
        if not self.__validate_block_hash_target():
            return False
        if not self.__validate_complete_account_balances():
            return False
        return True

    def add_account(self, account):
        self._accounts[account.id] = account

    def get_account_balances(self):
        return [{'id': account.id, 'balance': account.balance} for account in self._accounts.values()]

    def negative_bal_check(self, transactions, tmp_dict):
        for txn in transactions:
            sender = txn['message']['sender']
            amount = txn['message']['value']
            receiver = txn['message']['receiver']

            tmp_dict[sender] -= amount
            tmp_dict[receiver] += amount

        if any(bal < 0 for bal in iter(tmp_dict.values())):
            return True
