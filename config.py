#把你的API信息交出来 谢谢
# config.py
import os

API_CONFIG = {
    'apiKey': os.getenv('BITGET_API_KEY', '你的_API_KEY'),
    'secret': os.getenv('BITGET_SECRET_KEY', '你的_SECRET_KEY'),
    'password': os.getenv('BITGET_PASSPHRASE', '你的_PASSPHRASE_口令'),
    'timeout': 30000,
    'options': {    
        'defaultType': 'swap', #or 'spot'
    },
    'httpProxy': 'http://127.0.0.1:9674', 
    # 查询历史订单用不到wsProxy
}