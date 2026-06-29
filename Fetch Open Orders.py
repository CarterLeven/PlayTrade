#获取挂单状态
import asyncio
import ccxt.pro as ccxtpro  # 引入支持WebSocket的ccxt

# 1. 配置你的 Bitget API 凭证
API_CONFIG = {
    'apiKey': 'BITGET_API_KEY',
    'secret': '',
    'password': 'BITGET_PASSPHRASE',
    'timeout': 30000,  # 普通请求超时时间，单位毫秒
    'options': {    
        'defaultType': 'swap',
        'ws': {
            "options": {
                'timeout': 30000,  # WebSocket 超时时间
            }
        }
    },

    'httpProxy': '', 
    'wsProxy': '',
}

# 本地挂单状态缓存字典
local_orders = {}

def print_local_orders():
    print("\n" + "="*50)
    print(f" 当前活跃挂单总数: {len(local_orders)} ")
    print("="*50)
    if not local_orders:
        print("暂无挂单")
    for order_id, info in local_orders.items():
        print(f"【{info['symbol']}】| 方向: {info['side']} | 价格: {info['price']} | 数量: {info['amount']} | 已成交: {info['filled']}")
    print("="*50 + "\n")

async def monitor_orders():
    # 2. 初始化 Bitget 的 WebSocket 实例
    exchange = ccxtpro.bitget(API_CONFIG)
    
    print("正在连接 Bitget WebSocket 并获取初始挂单...")
    
    try:
        # 3. 先通过 REST API 获取一次当前的初始挂单，存入本地
        # fetch_open_orders 会自动处理
        initial_orders = await exchange.fetch_open_orders()
        for order in initial_orders:
            local_orders[order['id']] = order
        
        print(" 初始挂单同步成功！")
        print_local_orders()

        # 4. 进入无限循环，实时监听变动
        while True:
            # watch_orders 是 ccxtpro 提供的 WebSocket 私有频道监听方法
            # 它会保持长连接，当有订单变动时，该方法才会返回数据（非阻塞）
            orders = await exchange.watch_orders()
            
            for order in orders:
                order_id = order['id']
                status = order['status']  # 'open', 'closed', 'canceled'
                symbol = order['symbol']
                
                print(f"🔔 收到订单变动通知！订单ID: {order_id} | 币种: {symbol} | 当前状态: {status}")
                
                if status == 'open':
                    # 挂单中，或者部分成交但仍存活
                    local_orders[order_id] = order
                    print(f" 挂单更新/新增: 【{symbol}】以 {order['price']} 挂单 {order['amount']}")
                
                elif status in ['closed', 'canceled']:
                    # 订单完全成交(closed) 或 被撤单(canceled)
                    if order_id in local_orders:
                        del local_orders[order_id]
                    
                    action = "完全成交" if status == 'closed' else "已撤单"
                    print(f"❌ 挂单解除: 【{symbol}】该笔订单 {action}，已从本地同步移除。")
            
            # 变动后重新打印最新状态
            print_local_orders()

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 记得关闭连接
        await exchange.close()

if __name__ == "__main__":
    # 启动异步事件循环
    asyncio.run(monitor_orders())