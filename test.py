import asyncio

import aiohttp
from aiohttp import ClientTimeout
from web3 import AsyncWeb3, Web3, AsyncHTTPProvider

from CONSTANT import RPC
from IncludeAsync.AsyncTaskQueue import AsyncTaskQueue


class AsyncDoTask:
    def __init__(self, name, result):
        self.name = name  # Tên của tác vụ
        self.result = result  # Dữ liệu liên quan đến tác vụ, ví dụ URL

    async def run(self):
        """
        Hàm thực hiện công việc không đồng bộ (giả lập bằng asyncio.sleep).
        Bạn có thể thay thế bằng các logic async thực tế như gọi API.
        """
        try:
            l_ProxyAddress = "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"
            print(f"{self.name} is starting with result: {self.result}")
            # Giả lập tác vụ I/O không đồng bộ, ví dụ như gửi request API
            # l_web3_Linea = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.OP_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
            #                                                                               total=6000)}))
            # balance = await l_web3_Linea.eth.get_balance(Web3.to_checksum_address("0xb77216d362543396cb37163fbe7a30ce0723a375"))

            l_address = Web3.to_checksum_address("0xb77216d362543396cb37163fbe7a30ce0723a375")
            async with aiohttp.ClientSession() as session:
                l_web3_Base = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.BASE_RPC, request_kwargs={'proxy': l_ProxyAddress}))
                await l_web3_Base.provider.cache_async_session(session=session)
                l_bal_base = await l_web3_Base.eth.get_balance(l_address)

                l_web3_OP = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.OP_RPC, request_kwargs={'proxy': l_ProxyAddress}))
                await l_web3_OP.provider.cache_async_session(session=session)
                l_bal_OP = await l_web3_OP.eth.get_balance(l_address)

                l_web3_Scroll = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.SCROLL_RPC, request_kwargs={'proxy': l_ProxyAddress}))
                await l_web3_Scroll.provider.cache_async_session(session=session)
                l_bal_Scroll = await l_web3_Scroll.eth.get_balance(l_address)

                l_web3_arb = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.ARB_RPC, request_kwargs={'proxy': l_ProxyAddress}))
                await l_web3_arb.provider.cache_async_session(session=session)
                l_bal_arb = await l_web3_arb.eth.get_balance(l_address)

                l_web3_Linea = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.LINEA_RPC, request_kwargs={'proxy': l_ProxyAddress}))
                await l_web3_Linea.provider.cache_async_session(session=session)
                l_bal_Linea = await l_web3_Linea.eth.get_balance(l_address)

                balance = l_bal_Linea + l_bal_arb + l_bal_Scroll + l_bal_OP + l_bal_base
            print(f"{self.name} {balance}")
        except Exception as e:
            print(f"Error in {self.name}: {e}")

# class AsyncTaskQueue:
#     def __init__(self, max_concurrent_tasks=5):
#         # Hàng đợi để chứa các tác vụ
#         self.task_queue = asyncio.Queue()
#         # Số lượng tác vụ chạy đồng thời tối đa
#         self.max_concurrent_tasks = max_concurrent_tasks
#
#     async def worker(self):
#         """
#         Hàm để xử lý từng tác vụ (gọi phương thức `run` của `AsyncDoTask`).
#         """
#         while True:
#             # Lấy tác vụ từ hàng đợi (sẽ chờ đợi nếu không có tác vụ)
#             task_obj = await self.task_queue.get()
#
#             try:
#                 # Xử lý tác vụ
#                 await task_obj.run()
#             finally:
#                 # Báo cáo tác vụ đã hoàn thành
#                 self.task_queue.task_done()
#
#     def add_task(self, task_obj):
#         """
#         Thêm một tác vụ vào hàng đợi.
#         """
#         self.task_queue.put_nowait(task_obj)
#
#     async def run(self):
#         """
#         Khởi động nhiều worker để xử lý các tác vụ.
#         """
#         # Tạo nhiều worker để xử lý đồng thời các tác vụ
#         workers = [asyncio.create_task(self.worker()) for _ in range(self.max_concurrent_tasks)]
#         # Chờ cho đến khi hàng đợi được hoàn thành
#         await self.task_queue.join()
#         # Hủy bỏ các worker sau khi hoàn thành công việc
#         for worker in workers:
#             worker.cancel()

# Hàm để khởi tạo và thêm tác vụ vào hàng đợi
async def main():
    # Giả sử l_Results là danh sách các URL hoặc địa chỉ để thực hiện tác vụ
    l_Results = [
        [
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://jsonplaceholder.typicode.com/posts/2",
            "https://jsonplaceholder.typicode.com/posts/3",
            "https://jsonplaceholder.typicode.com/posts/4",
            "https://jsonplaceholder.typicode.com/posts/5"
        ],
        [
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://jsonplaceholder.typicode.com/posts/2",
            "https://jsonplaceholder.typicode.com/posts/3",
            "https://jsonplaceholder.typicode.com/posts/4",
            "https://jsonplaceholder.typicode.com/posts/5"
        ],
    ]*100

    # Tạo một hàng đợi xử lý với giới hạn tối đa 20 tác vụ đồng thời
    task_queue = AsyncTaskQueue(max_concurrent_tasks=100)

    # Thêm 20 tác vụ vào hàng đợi
    for i in range(0, 200):
        task_obj = AsyncDoTask(f"Task {i}", l_Results[i])  # Khởi tạo đối tượng AsyncDoTask
        task_queue.add_task(task_obj)  # Thêm tác vụ vào hàng đợi
        # await asyncio.sleep(0.1)  # Giả lập việc thêm tác vụ theo thời gian thực

    # Khởi động hệ thống xử lý tác vụ
    await task_queue.run()

# Chạy asyncio
asyncio.run(main())
