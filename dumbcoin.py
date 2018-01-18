import time
import json
from hashlib import sha256

class BlockchainException(Exception):
    pass

class Block():

    def __init__(self, index, timestamp, transactions, proof, previous_block):

        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_block = previous_block
        self.hash = self.get_hash()

    def get_hash(self):

        if self.transactions:
            block_string = "{}{}{}".format(self.index,
                                           self.timestamp,
                                           json.dumps(self.transactions))
        else:
            block_string = "{}{}".format(self.index,
                                         self.timestamp)

        hash_value = sha256(block_string.encode()).hexdigest()
        return hash_value

    def verify_block(self):
        verification_hash = sha256("{}{}".format(self.hash,
                                                 self.proof).encode()).hexdigest()
        return verification_hash[:4] == "0000"

    def __str__(self):
        string_template = "Block: {},\nTime: {},\nProof: {},\nTransactions: {}\n"
        return string_template.format(self.index,
                                      self.timestamp,
                                      self.proof,
                                      self.transactions)

class Blockchain():

    def __init__(self):
        self.transactions = []
        self.last_block = Blockchain.create_genesis_block()

    def add_transaction(self, sender, recipient, amount, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        transaction = {"sender": sender,
                       "recipient": recipient,
                       "amount": amount,
                       "timestamp": timestamp}
        self.transactions.append(transaction)

    def add_block(self):
        if not self.transactions:
            raise BlockchainException("No transactions to add to block")
        new_block = Blockchain.mine_block(self.transactions, self.last_block)
        self.last_block = new_block

    def verify_blockchain(self):
        block = self.last_block
        def recursive_verify(block):
            if block.verify_block():
                if block.previous_block:
                    recursive_verify(block.previous_block)
                else:
                    return True
            else:
                return False

        return recursive_verify(block)

    def print_blockchain(self):
        block = self.last_block
        def recursive_print(block):
            print(block)
            if block.previous_block:
                recursive_print(block.previous_block)
        recursive_print(block)

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
    def create_genesis_block():
        index = 0
        timestamp = time.time()

        genesis_hash = sha256("{}{}".format(index,
                                            timestamp).encode()).hexdigest()
        proof = Blockchain.get_proof(genesis_hash)
        genesis_block = Block(index, timestamp, None, proof, None)
        return genesis_block

    @staticmethod
    def mine_block(data, previous_block):
        index = previous_block.index + 1
        timestamp = time.time()
        block_string = "{}{}{}".format(index,
                                       timestamp,
                                       json.dumps(data))
        block_hash = sha256(block_string.encode()).hexdigest()
        proof = Blockchain.get_proof(block_hash)
        new_block = Block(index, timestamp, data, proof, previous_block)
        return new_block
