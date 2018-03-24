import json
from evm.rlp.headers import (
    BlockHeader,
    CollationHeader,
)

from evm.db.chain import ChainDB
from evm import db

from evm.vm.forks.tangerine_whistle.vm_state import TangerineWhistleVMState
from evm.vm.forks import TangerineWhistleVM

from evm.tools import fixture_tests
from eth_keys import keys

transaction_string = '''
{
    "env" : 
    {
        "currentCoinbase" : "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        "currentDifficulty" : "0x20000",
        "currentGasLimit" : "0x174876e800",
        "currentNumber" : "0x01",
        "currentTimestamp" : "0x03e8",
        "previousHash" : "0x5e20a0453cecd065ea59c37ac63e079ee08998b6045136a8ce6635c7912ec0b6"
    },
    "EIP150" : {
        "hash" : "0x7e7ff82e1c33ffbeb3dedb679498c9716f83c697f497d75aca467ae936b8ae45",
        "logs" : "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347"
    }, 
    "pre" : {
            "0x6a0a0fc761c612c340a0e98d33b37a75e5268472" : {
                "balance" : "0x0de0b6b3a7640000",
                "code" : "0x7f6004600c60003960046000f3600035ff00000000000000000000000000000000600052602060006000f0600054805b6001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1506001018060005260008060208180876006f1505a616000106200002f57600055",
                "nonce" : "0x00",
                "storage" : {
                }
            },
            "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {
                "balance" : "0xe8d4a51000",
                "code" : "",
                "nonce" : "0x00",
                "storage" : {
                }
            }
    },
    "transaction" : {
        "data" : [
            ""
        ],
        "gasLimit" : [
            "0x0c3500"
        ],
        "gasPrice" : "0x01",
        "nonce" : "0x00",
        "secretKey" : "0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8",
        "to" : "0x6a0a0fc761c612C340a0e98d33b37a75e5268472",
        "value" : [
            "0x00"
        ]
    }
} 
'''

transaction_obj = json.loads(transaction_string)


def get_ancestor_block_hash(self, block_number):
    if block_number >= self.block_number:
        return b''
    elif block_number < 0:
        return b''
    elif block_number < self.block_number - 256:
        return b''
    else:
        return keccak(text="{0}".format(block_number))

def get_prev_hashes(self, last_block_hash, db):
    return []


_tangerineWhistleVMState = TangerineWhistleVMState.configure(
    get_ancestor_hash=get_ancestor_block_hash
)

_tangerineWhistleVM = TangerineWhistleVM.configure(
    _state_class=_tangerineWhistleVMState,
    get_prev_hashes=get_prev_hashes,
)

def normalize_state(obj):
    normalized = {
        'env': fixture_tests.normalize_environment(obj['env']),
        'pre': fixture_tests.normalize_account_state(obj['pre']),
        'transaction': fixture_tests.normalize_unsigned_transaction(obj['transaction'],obj["EIP150"])
    }

    return normalized

normalize_obj  = normalize_state(transaction_obj)


def transaction_test(normalize_obj):
    header = BlockHeader(
        coinbase=transaction_obj['env']['currentCoinbase'],
        difficulty=transaction_obj['env']['currentDifficulty'],
        block_number=transaction_obj['env']['currentNumber'],
        gas_limit=transaction_obj['env']['currentGasLimit'],
        timestamp=transaction_obj['env']['currentTimestamp'],
        parent_hash=transaction_obj['env']['previousHash']
    )

    chaindb = ChainDB(db.get_db_backend()) #defult memeory db

    vm = _tangerineWhistleVM(header=header, chaindb=chaindb)
    with vm.state.mutable_state_db() as state_db:
        state_db.apply_state_dict(normalize_obj['pre'])
    vm.block.header.state_root = vm.state.state_root
    unsigned_transaction = vm.create_unsigned_transaction(
        nonce=normalize_obj['transaction']['nonce'],
        gas_price=normalize_obj['transaction']['gasPrice'],
        gas=normalize_obj['transaction']['gasLimit'],
        to=normalize_obj['transaction']['to'],
        value=normalize_obj['transaction']['value'],
        data=normalize_obj['transaction']['data'],
    )
    private_key = keys.PrivateKey(normalize_obj['transaction']['secretKey'])
    transaction = unsigned_transaction.as_signed_transaction(private_key=private_key)
    return transaction

result = transaction_test(normalize_obj)
