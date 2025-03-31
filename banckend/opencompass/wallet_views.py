from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from web3 import Web3
from eth_account.messages import encode_defunct
import json
from django.conf import settings
from datetime import datetime, timedelta
import jwt

# 连接到以太坊网络
w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/86fa8d2d26f7440aa9ca5504cbc7e095'))

# 合约地址
CONTRACT_ADDRESS = '0x2Ce142f6A1997432F8055c135A046963F7769F55'

# 合约ABI
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "string", "name": "_description", "type": "string"},
            {"internalType": "string", "name": "_category", "type": "string"},
            {"internalType": "string", "name": "_ipfsHash", "type": "string"},
            {"internalType": "string", "name": "_previewHash", "type": "string"},
            {"internalType": "uint256", "name": "_price", "type": "uint256"},
            {"internalType": "enum ModelStructs.ModelLicense", "name": "_license", "type": "uint8"}
        ],
        "name": "registerModel",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

@csrf_exempt
@require_http_methods(["POST"])
def verify_wallet(request):
    """验证钱包地址和签名"""
    try:
        data = json.loads(request.body)
        address = data.get('address')
        signature = data.get('signature')
        nonce = data.get('nonce')

        # 验证必要参数
        if not all([address, signature, nonce]):
            return JsonResponse({
                'success': 'false',
                'message': 'Missing required parameters'
            }, status=400)

        # 验证地址格式
        if not w3.is_address(address):
            return JsonResponse({
                'success': 'false',
                'message': 'Invalid Ethereum address'
            }, status=400)

        # 构造消息
        message = f"Sign this message to verify your wallet ownership. Nonce: {nonce}"
        message_hash = encode_defunct(text=message)
        
        try:
            # 恢复签名者地址
            recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
            
            # 验证地址匹配
            if recovered_address.lower() != address.lower():
                return JsonResponse({
                    'success': 'false',
                    'message': 'Invalid signature'
                }, status=401)

            # 生成JWT token
            token = generate_token(address)

            return JsonResponse({
                'success': 'true',
                'message': 'Wallet verified successfully',
                'data':{
                    'address': address,
                    'token': token
                }
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid signature format'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def generate_token(address):
    """生成JWT token"""
    payload = {
        'address': address,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

@csrf_exempt
def get_wallet_balance(request):
    """获取钱包余额"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        address = data.get('address')

        if not w3.is_address(address):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid Ethereum address'
            }, status=400)

        # 获取ETH余额
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')

        return JsonResponse({
            'status': 'success',
            'balance': str(balance_eth),
            'address': address
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def get_transaction_history(request):
    """获取交易历史"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        address = data.get('address')
        limit = data.get('limit', 10)  # 默认获取10条记录

        if not w3.is_address(address):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid Ethereum address'
            }, status=400)

        # 获取最新的区块号
        latest_block = w3.eth.block_number
        transactions = []

        # 获取交易历史
        for i in range(limit):
            try:
                block = w3.eth.get_block(latest_block - i, full_transactions=True)
                for tx in block.transactions:
                    if tx['to'] and tx['to'].lower() == address.lower() or \
                       tx['from'].lower() == address.lower():
                        transactions.append({
                            'hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': str(w3.from_wei(tx['value'], 'ether')),
                            'block': block.number,
                            'timestamp': block.timestamp
                        })
            except Exception as e:
                print(f"Error processing block {latest_block - i}: {str(e)}")

        return JsonResponse({
            'status': 'success',
            'transactions': transactions,
            'address': address
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def send_transaction(request):
    """发送交易"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        from_address = data.get('from')
        to_address = data.get('to')
        value = data.get('value')  # in ETH
        signed_transaction = data.get('signedTransaction')

        if not all([from_address, to_address, value, signed_transaction]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            }, status=400)

        # 验证地址
        if not w3.is_address(from_address) or not w3.is_address(to_address):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid Ethereum address'
            }, status=400)

        # 发送已签名的交易
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_transaction)
            return JsonResponse({
                'status': 'success',
                'transaction_hash': tx_hash.hex(),
                'message': 'Transaction sent successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Transaction failed: {str(e)}'
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
