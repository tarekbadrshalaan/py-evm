from evm import constants, Chain
from evm.vm.forks.frontier import FrontierVM
from evm.vm.forks.homestead import HomesteadVM
from evm.chains.mainnet import HOMESTEAD_MAINNET_BLOCK 

from evm.db.backends.memory import MemoryDB
from evm.db.chain import ChainDB
from evm.chains.mainnet import MAINNET_GENESIS_HEADER

import json

#chain.create_transaction

chain_class = Chain.configure(
  __name__='Test Chain',
  vm_configuration=(
      (constants.GENESIS_BLOCK_NUMBER, FrontierVM),
      (HOMESTEAD_MAINNET_BLOCK, HomesteadVM),
  ),
)  
# start a fresh in-memory db
chaindb = ChainDB(MemoryDB()) 
# initialize a fresh chain
chain = chain_class.from_genesis_header(chaindb, MAINNET_GENESIS_HEADER) 
vm = chain.get_vm() 
transaction_json = '''{"transaction":{
            "data" : "",
            "gasLimit" : "0x5208",
            "gasPrice" : "0x01",
            "nonce" : "0x00",
            "r" : "0x01",
            "s" : "0x1fffd310ac743f371de3b9f7f9cb56c0b28ad43601b4ab949f53faa07bd2c804",
            "to" : "0x095e7baea6a6c7c4c2dfeb977efac326af552d87",
            "v" : "0x1b",
            "value" : "0x0b"
        }}''' 
 
transaction_obj = json.loads(transaction_json)

vm.create_transaction(transaction_obj)