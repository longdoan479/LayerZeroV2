import asyncio
import time

import aiohttp
import requests
from hexbytes import HexBytes
from web3 import Web3, AsyncWeb3

from CONSTANT import RPC

http_proxy = {
    "http": "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80",
    "https": "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"
}

# Tạo một session với proxy
session = requests.Session()
session.proxies.update(http_proxy)


starttime = time.time()
for i in range(0, 10):
    l_web3_Base = Web3(Web3.HTTPProvider(RPC.BASE_RPC, session=session))
    l_web3_OP = Web3(Web3.HTTPProvider(RPC.OP_RPC, session=session))
    l_web3_Scroll = Web3(Web3.HTTPProvider(RPC.SCROLL_RPC, session=session))
    l_web3_Linea = Web3(Web3.HTTPProvider(RPC.LINEA_RPC, session=session))
    l_web3_arb = Web3(Web3.HTTPProvider(RPC.ARB_RPC, session=session))
    l_bal_base = l_web3_Base.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_OP = l_web3_OP.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_Scroll = l_web3_Scroll.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_Linea = l_web3_Linea.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_arb = l_web3_arb.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
endtime = time.time()

print(endtime-starttime)




async def get_latest_balance():

    starttime = time.time()
    # for i in range(0, 10):
    l_web3_Base2 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.BASE_RPC, request_kwargs={'proxy': "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"}))
    l_web3_OP2 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.OP_RPC, request_kwargs={'proxy': "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"}))
    l_web3_Scroll2 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.SCROLL_RPC, request_kwargs={'proxy': "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"}))
    l_web3_Linea2 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.LINEA_RPC, request_kwargs={'proxy': "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"}))
    l_web3_arb2 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.ARB_RPC, request_kwargs={'proxy': "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"}))

    l_bal_base2 = await l_web3_Base2.eth.get_balance(
        Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_OP2 = await l_web3_OP2.eth.get_balance(Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_Scroll2 = await l_web3_Scroll2.eth.get_balance(
        Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_Linea2 = await l_web3_Linea2.eth.get_balance(
        Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    l_bal_arb2 = await l_web3_arb2.eth.get_balance(
        Web3.to_checksum_address("0x1d3eea5083edba99708c431d2bb81b1c76613b9e"))
    endtime = time.time()
    print(endtime - starttime)


# Chạy hàm bất đồng bộ
# asyncio.run(get_latest_balance())


# Hàm khởi chạy tất cả các tác vụ không đồng bộ
async def main():
    tasks = []

    # Tạo và thêm các tác vụ vào danh sách tasks
    for i in range(20):
        # Tạo đối tượng AsyncDoTask và chạy task
        # task_obj = AsyncDoTask(f"Task {i + 1}", l_Results[i])
        task = asyncio.create_task(get_latest_balance())  # Chạy tác vụ không đồng bộ
        tasks.append(task)

    # Đợi tất cả các tác vụ hoàn thành
    await asyncio.gather(*tasks)


# Chạy chương trình asyncio
asyncio.run(main())
