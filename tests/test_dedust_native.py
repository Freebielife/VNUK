import copy
import json
import unittest
from pathlib import Path
from dedust_native import rows

POOL = 'EQAgujoYOUx4Ws5x8WhVLIi4_79lbYenvPbDz3tYjz3j4gln'
EVENTS = json.loads((Path(__file__).parent / 'fixtures/dedust-events.json').read_text())['events']

class DeDustNativeTests(unittest.TestCase):
    def test_real_sell_and_buy(self):
        sell = list(rows(EVENTS[0], POOL))[0]
        buy = list(rows(EVENTS[1], POOL))[0]
        self.assertEqual((sell['kind'], sell['tokenAmount'], sell['ton']), ('sell', '37500', '4.511081337'))
        self.assertEqual((buy['kind'], buy['tokenAmount'], buy['ton']), ('buy', '33070.763337239', '4'))

    def test_failed_missing_ambiguous_payout(self):
        for mode in ('failed', 'missing', 'duplicate'):
            e = copy.deepcopy(EVENTS[0])
            if mode == 'failed': e['actions'][1]['status'] = 'failed'
            if mode == 'missing': e['actions'].pop()
            if mode == 'duplicate': e['actions'].append(copy.deepcopy(e['actions'][1]))
            self.assertEqual(list(rows(e, POOL)), [], mode)

    def test_wrong_recipient_and_multi_hop(self):
        for old, new in [('Next: null', 'Next: {}'), ('RecipientAddr: ""', 'RecipientAddr: 0:' + 'f'*64)]:
            e = copy.deepcopy(EVENTS[0])
            e['actions'][0]['SmartContractExec']['payload'] = e['actions'][0]['SmartContractExec']['payload'].replace(old, new)
            self.assertEqual(list(rows(e, POOL)), [])

    def test_in_progress_and_other_pool(self):
        e = copy.deepcopy(EVENTS[0]); e['in_progress'] = True
        self.assertEqual(list(rows(e, POOL)), [])
        self.assertEqual(list(rows(EVENTS[0], '0:' + 'a'*64)), [])
