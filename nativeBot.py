from web3 import *
import time
import sys
import re

chains_param = {
    'arb': [
        'https://rpc.arb1.arbitrum.gateway.fm',
        'https://arbitrum-one.publicnode.com',
        'https://arbitrum.blockpi.network/v1/rpc/public',
        'https://arbitrum.meowrpc.com',
        'https://endpoints.omniatech.io/v1/arbitrum/one/public',
        'https://arbitrum-one.public.blastapi.io',
        'https://arb-mainnet-public.unifra.io',
        'https://arb1.croswap.com/rpc',
        'https://api.zan.top/node/v1/arb/one/public',
        'https://arb1.arbitrum.io/rpc',
        'https://rpc.ankr.com/arbitrum',
        'https://1rpc.io/arb',
        'https://arbitrum.api.onfinality.io/public',
    ],
}

rpc_index = 0

privateKeys = []

def getETHBalance(private_key):
    try:
        global rpc_index
        w3 = Web3(Web3.HTTPProvider(chains_param['arb'][rpc_index]))
        address = w3.eth.account.from_key(private_key).address
        response = w3.eth.get_balance(Web3.to_checksum_address(address))
        print(response)
        return { 'success': True, 'balance': response, 'error': None }
    except Exception as error:
        # if str(error).find('429') != -1:
        if rpc_index < (len(chains_param['arb']) - 1):
            rpc_index += 1
        else:
            rpc_index = 0
        return { 'success': False, 'balance': None, 'error': error }

def transfer_eth_all_arb(recipient, amount, private_key, gas = 210000):
    try:
        chain = 'arb'
        w3 = Web3(Web3.HTTPProvider(chains_param['arb'][rpc_index]))
        from_address = w3.eth.account.from_key(private_key).address
        gasPrice = int(w3.eth.gas_price * 1.2)
        if amount - int(gasPrice * gas) < 0:
            return {
                'success': False,
                'txHash': None,
                'error': 'value + gas more then balance'
            }

        transaction = {
            'chainId': 42161,
            'from': from_address,
            'value': int(amount - int(gasPrice * gas)),
            'to': recipient,
            'gas': gas,
            'gasPrice': gasPrice,
            'nonce': w3.eth.get_transaction_count(w3.eth.account.from_key(private_key).address),
        }
        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txHash = transaction_hash.hex()
        print('send money')
        return {
            'success': True,
            'txHash': txHash,
            'error': None
        }
    except Exception as error:
        if 'message' in error.args[0]:
            if error.args[0]['message'] == 'intrinsic gas too low':
                recurs_data = transfer_eth_all_arb(chain, recipient, amount, private_key, int(gas + 50000))
                return recurs_data
            else:
                print(f'send error: {error}')
                return {
                    'success': False,
                    'txHash': None,
                    'error': error
                }
        else:
            print(f'send error: {error}')
            return {
                'success': False,
                'txHash': None,
                'error': error
            }

def start(chain, private_key, recipient):
    if chain == 'arb':
        balance = getETHBalance(private_key)
        if balance['success'] and balance['balance'] > 5000000000000:
            transfer_eth_all_arb(recipient, balance['balance'], private_key)


if __name__ == "__main__":
    print('start')
    # chain = sys.argv[1]

    chain = 'arb'

    with open('privateKay.txt') as f:
        while True:
            line = f.readline()
            if not line:
                break
            privateKeys.append(re.sub(r"\s+", "", line))

    while True:
        with open('privateKay.txt') as f:
            recipient = re.sub(r"\s+", "", f.readline())

        for privateKay in privateKeys:
            start(chain, privateKay, recipient)
        time.sleep(2)

# while True:
#     getETHBalance('8719904fd581e4e85469b6a4e3f94a86dcbc9ede63fa95c68522f11916ae16ab')
#     time.sleep(2)