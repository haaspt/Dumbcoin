import time
import json
from timeit import default_timer as timer
from hashlib import sha256

class BlockchainException(Exception):
    pass

class Block():
    """
    A cryptographically secured block of data that forms the basis of a
    blockchain. The integrity of the block and its contents can be verified by
    checking that the hash of its contents and proof pass a predetermined
    verification test. Each block links back to the previous block in the chain,
    forming a singly linked list.

    Parameters
    ----------
    index : int
        The index of the current block within the blockchain array
    timestamp : float or datetime-like
        Timestamp when the block was mined
    transactions : json-like or serializable
        A serializable block of data whose contents are cryptographically secured
    proof : int
        A number that, when hashed along with the current block's hash, will
        produce a string whose first 4 bytes are 0s. A valid proof is required
        for instantiation.
    previous_block : Block
        A reference to the previous block in the blockchain. The first block is
        initialized with None.

    Examples
    --------
    >>> block = Block(0,
    ...               1516311858.4676182,
    ...               [{"sender", None,
    ...                 "recipient", "genesis",
    ...                 "amount": 1000,
    ...                 "timestamp": 1516311858.4676182}],
    ...               172352,
    ...               None)
    >>> block.verify_block()
    True

    Raises
    ------
    BlockchainException
        when a block does not pass verification
    """

    def __init__(self, index, timestamp, transactions, proof, previous_block):

        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_block = previous_block
        self.hash = self.get_hash()
        if not self.verify_block():
            raise BlockchainException("Block failed verification on init")

    def get_hash(self):
        """
        Produces a hash string of the contents of the current block for
        cryptographic security. Hash is based on a concatenated string of the
        block's index, timestamp, and transaction data.

        Returns
        -------
        hash_value : string
        """
        block_string = "{}{}{}".format(self.index,
                                       self.timestamp,
                                       json.dumps(self.transactions))

        hash_value = sha256(block_string.encode()).hexdigest()
        return hash_value

    def verify_block(self):
        """
        Verifies if the current block is valid. Hashes the combined string of
        the block's hash along with the proof. It then checks if the first four
        bytes of the verification hash are 0s (which is the convention of this
        blockchain).

        Returns
        -------
        block_verified : boolean
        """
        verification_hash = sha256("{}{}".format(self.hash,
                                                 self.proof).encode()).hexdigest()
        block_verified = verification_hash[:4] == "0000"
        return block_verified

    def __str__(self):
        string_template = "Block: {},\nTime: {},\nProof: {},\nTransactions: {}\n"
        return string_template.format(self.index,
                                      self.timestamp,
                                      self.proof,
                                      self.transactions)

class Blockchain():
    """
    An object to assist with the creation and tracking of a blockchain. The
    object itself stores parameters allowing transactions to be queued before
    being added to a block, and a reference to the last block in the chain.

    The blockchain itself is a singly linked list of Block objects which can be
    traversed starting with the `last_block` parameter. Class methods support
    the initialization of new blockchains, the recording of transactions, etc.
    While static methods support utility functions for creating new blocks,
    which can be used without instantiating the class.

    Parameters
    ----------
    transactions : list of dicts
        A record of transactions that have not yet been added to a block
    seed_amount : int, optional
        The initial amount of coins available when a genesis block is created.
        Defaults to 1,000 if not specified.
    last_block : Block
        A reference to the last block in the blockchain array

    Examples
    --------
    >>> dumbcoin = Blockchain(seed_amount=2000)
    >>> dumbcoin.verify_blockchain()
    True
    """
    def __init__(self, seed_amount=1000):
        self.transactions = []
        self.seed_amount = seed_amount
        self.last_block = Blockchain.create_genesis_block(self.seed_amount)

    def add_transaction(self, sender, recipient, amount, timestamp=None, validate_transaction=True):
        if not timestamp:
            timestamp = time.time()
        transaction = {"sender": sender,
                       "recipient": recipient,
                       "amount": amount,
                       "timestamp": timestamp}
        print("Staging transaction: {}".format(transaction))
        if validate_transaction:
            validated = Blockchain.validate_transaction(transaction,
                                                        Blockchain.get_settled_transactions(self.last_block))
            if not validated:
                raise BlockchainException("Transaction failed to validate. Aborting")
            print("Transaction validated against ledger")
        self.transactions.append(transaction)
        print("Transaction stagged. {} transactions awaiting mining".format(len(self.transactions)))

    def add_block(self):
        if not self.transactions:
            raise BlockchainException("No transactions to add to block")
        print("Mining new block with {} transactions".format(len(self.transactions)))
        new_block = Blockchain.mine_block(self.transactions, self.last_block)
        self.transactions = []
        self.last_block = new_block
        print("Block successfully added to blockchain at index {}".format(new_block.index))

    @staticmethod
    def verify_blockchain(last_block):
        last_block
        def recursive_verify(block):
            if block.verify_block():
                if block.previous_block:
                    return recursive_verify(block.previous_block)
                else:
                    return True
            else:
                return False
        return recursive_verify(last_block)

    @staticmethod
    def get_settled_transactions(last_block):
        transaction_list = []
        def recursive_transactions(block):
            for transaction in block.transactions:
                transaction_list.append(transaction)
            if block.previous_block:
                recursive_transactions(block.previous_block)
            else:
                return
        recursive_transactions(last_block)
        transaction_list.sort(key=(lambda x: x['timestamp']), reverse=False)
        return transaction_list

    @staticmethod
    def get_proof(block_hash):
        proof = 0
        proof_found = False
        while not proof_found:
            proof_hash = sha256("{}{}".format(block_hash,
                                              proof).encode()).hexdigest()
            if proof_hash[:4] == "0000":
                proof_found = True
                break
            proof += 1
        return proof

    @staticmethod
    def create_genesis_block(seed_amount):
        index = 0
        timestamp = time.time()
        transactions = [{"sender": None,
                         "recipient": "genesis",
                         "amount": seed_amount,
                         "timestamp": timestamp}]

        genesis_hash = sha256("{}{}{}".format(index,
                                            timestamp,
                                            json.dumps(transactions)).encode()).hexdigest()
        proof = Blockchain.get_proof(genesis_hash)
        genesis_block = Block(index, timestamp, transactions, proof, None)
        return genesis_block

    @staticmethod
    def mine_block(data, previous_block):
        process_start = timer()
        index = previous_block.index + 1
        timestamp = time.time()
        block_string = "{}{}{}".format(index,
                                       timestamp,
                                       json.dumps(data))
        block_hash = sha256(block_string.encode()).hexdigest()
        proof = Blockchain.get_proof(block_hash)
        new_block = Block(index, timestamp, data, proof, previous_block)
        process_end = timer()
        print("New block at index {} mined in {}s".format(new_block.index,
                                                          (process_end-process_start)))
        return new_block

    @staticmethod
    def create_ledger(past_transactions):
        ledger = {}
        # Check the first block to make sure it's a genesis block
        genesis_block = past_transactions[0]
        if genesis_block['recipient'] is not 'genesis' and genesis_block['sender'] is not None:
            raise BlockchainException("Valid genesis block not found")
        # Set initial genesis value in ledger
        ledger[genesis_block['recipient']] = genesis_block['amount']
        # Iterate through the rest of the transactions and fill in the ledger
        for transaction in past_transactions[1:]:
            ledger = Blockchain.add_transaction_to_ledger(transaction, ledger)

        return ledger

    @staticmethod
    def add_transaction_to_ledger(transaction, ledger):
        sender = transaction['sender']
        recipient = transaction['recipient']
        amount = transaction['amount']
        if sender not in ledger.keys():
            raise BlockchainException("Sender {} made a transaction before appearing in the ledger".format(sender))
        if (ledger[sender] - amount) < 0:
            raise BlockchainException("Sender {} attempted to overdraw their coins".format(sender))
        if recipient not in ledger.keys():
            ledger[recipient] = 0
        ledger[sender] -= amount
        ledger[recipient] += amount

        return ledger

    @staticmethod
    def validate_transaction(new_transaction, past_transactions):
        print("Validating transaction: {}".format(new_transaction))
        ledger = Blockchain.create_ledger(past_transactions)
        try:
            Blockchain.add_transaction_to_ledger(new_transaction, ledger)
        except BlockchainException:
            return False

        return True

    def __str__(self):
        block_strings = []
        def recursive_strings(block):
            block_strings.append(block.__str__())
            if block.previous_block:
                recursive_strings(block.previous_block)
            else:
                return
        recursive_strings(self.last_block)
        blockchain_string = "\n".join(block_strings)
        return blockchain_string

    def __len__(self):
        return self.last_block.index + 1
