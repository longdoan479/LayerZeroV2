import asyncio
import random


from Include.FileProcessing import FileProcessing
import CONSTANT as Cons
from ThreadTask.AsyncDoTask import AsyncDoTask

from ThreadTask.ThreadDoTask import ThreadDoTask

l_FileProxy = FileProcessing("proxy.xlsx")
Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()

l_FileKey = FileProcessing("key.xlsx")

l_lstAccount = []
l_lstAccount.extend(l_FileKey.ReadData())


l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup

l_lstAccountRandom = []
groups_Account = {}

for i in range(1, l_MaxGroup+1):
    group = i

    l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == group, l_lstAccount))

    # Nhóm dữ liệu theo giá trị group
    if group not in groups_Account:
        groups_Account[group] = []

    random.shuffle(l_lstAccountFilter)
    groups_Account[group].extend(l_lstAccountFilter)

l_randomThreadNumber = random.randint(10, 13)

# Chia các nhóm thành 5 mảng
l_Results = [[] for _ in range(l_randomThreadNumber)]
group_list = list(groups_Account.values())

for i, group in enumerate(group_list):
    l_Results[i % l_randomThreadNumber].extend(group)

# Danh sách các luồng
threads = []


# Hàm khởi chạy tất cả các tác vụ không đồng bộ
async def main():
    tasks = []

    # Tạo và thêm các tác vụ vào danh sách tasks
    for i in range(l_randomThreadNumber):
        # Tạo đối tượng AsyncDoTask và chạy task
        task_obj = AsyncDoTask(f"Task {i + 1}", l_Results[i])
        task = asyncio.create_task(task_obj.run())  # Chạy tác vụ không đồng bộ
        tasks.append(task)

    # Đợi tất cả các tác vụ hoàn thành
    await asyncio.gather(*tasks)


# Chạy chương trình asyncio
asyncio.run(main())

#
# # Tạo và khởi động 20 luồng
# for i in range(l_randomThreadNumber):
#     # thread = threading.Thread(target=task, args=(i,))
#     thread = ThreadDoTask(f"Thread {i+1}", l_Results[i])
#     threads.append(thread)
#     thread.start()
#
# # Đảm bảo tất cả các luồng hoàn thành
# for thread in threads:
#     thread.join()