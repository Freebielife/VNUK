import unittest
import observatory

class ZeroAddressTest(unittest.TestCase):
    def test_zero_is_separate_from_wallet_holders(self):
        self.assertEqual(observatory.role('0:'+'0'*64, {'is_wallet': True}), 'Zero address')
