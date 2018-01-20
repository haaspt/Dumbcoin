import unittest
from dumbcoin import Blockchain, BlockchainException

class BlockchainTest(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain(2000)
    def test_blockchain_creation(self):
        self.assertTrue(self.blockchain.verify_blockchain())
        self.assertTrue(self.blockchain.verify_block(self.blockchain.last_block))

    def test_transaction_validation(self):
        with self.assertRaises(BlockchainException):
            self.blockchain.add_transaction("foo", "bar", 10)
        with self.assertRaises(BlockchainException):
            self.blockchain.add_transaction("genesis", "bar", 5000)
        with self.assertRaises(BlockchainException):
            self.blockchain.add_block()

    def test_block_creation(self):
        self.blockchain.add_transaction("genesis", "adam", 1000)
        self.blockchain.add_transaction("genesis", "eve", 1000)
        self.blockchain.add_block()
        self.assertTrue(self.blockchain.verify_blockchain())

if __name__ == '__main__':
    unittest.main()
