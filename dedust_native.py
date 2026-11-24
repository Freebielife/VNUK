"""Direct DeDust swaps when TonAPI exposes low-level pool actions.

Pool get_assets and both vault get_asset responses were checked on setup.
Only paired successful swap/payout calls with one hop and the same query ID
and recipient are accepted; routed/ambiguous calls are omitted.
"""
import re
from assets import raw_address, token_amount
from scripts.project_runtime import canonical_address

POOL = '0:20ba3a18394c785ace71f168552c88b8ffbf656d87a7bcf6c3cf7b588f3de3e2'
NATIVE = '0:dae153a74d894bbc32748198cd626e4f5df4a69ad2fa56ce80fc2644b5708d20'
JETTON = '0:b08a96aeeba5a5a04770b1d3b2900b1a6419cc7e9a6c452bc927405c16edb5d9'

def field(payload, name):
    match = re.search(r'^' + name + r':\s*"?([^"\n]+)"?\s*$', payload, re.M)
    return match.group(1).strip() if match else None

def rows(event, pool):
    if event.get('in_progress') or canonical_address(pool) != POOL:
        return
    calls = [a for a in event.get('actions', [])
             if a.get('type') == 'SmartContractExec' and a.get('status') == 'ok']
    for action in calls:
        call = action['SmartContractExec']
        payload = call.get('payload', '')
        if (call.get('operation') != 'DedustSwapExternal' or
            call['contract']['address'] != POOL or
            not re.search(r'^  Next: null$', payload, re.M)):
            continue
        source = call['executor']['address']
        if source not in (NATIVE, JETTON):
            continue
        sender = field(payload, 'SenderAddr')
        recipient = re.search(r'^  RecipientAddr: (.+)$', payload, re.M)
        if not sender or not recipient or recipient.group(1) not in ('""', sender):
            continue
        query = field(payload, 'QueryId')
        matches = []
        for payout in calls:
            out = payout['SmartContractExec']
            if (out.get('operation') == 'DedustPayoutFromPool' and
                out['executor']['address'] == POOL and
                out['contract']['address'] == (JETTON if source == NATIVE else NATIVE) and
                field(out.get('payload', ''), 'QueryId') == query and
                field(out.get('payload', ''), 'RecipientAddr') == sender):
                matches.append(out)
        if len(matches) != 1 or not query:
            continue
        amount_in = field(payload, 'Amount')
        amount_out = field(matches[0].get('payload', ''), 'Amount')
        tx = (action.get('base_transactions') or [''])[0]
        if (not amount_in or not amount_out or not amount_in.isdigit() or
            not amount_out.isdigit() or not re.fullmatch(r'[a-f0-9]{64}', tx)):
            continue
        if not int(amount_in) or not int(amount_out):
            continue
        buy = source == NATIVE
        yield {'kind': 'buy' if buy else 'sell', 'time': int(event['timestamp']),
               'tx': tx, 'lt': str(event['lt']), 'wallet': raw_address(sender),
               'tokenAmount': token_amount(amount_out if buy else amount_in),
               'ton': token_amount(amount_in if buy else amount_out),
               'dex': 'DeDust', 'pool': pool,
               'evidence': 'paired-dedust-swap-payout'}
