import os
import random
import time
import traceback
from datetime import datetime

import aiohttp
from aiohttp import ClientTimeout
from typing_extensions import List
from web3 import Web3, AsyncWeb3

from Include.Data import DataWallet
from IncludeAsync.AccountEVM import AccountEVM
from Logging import Logging
import CONSTANT as Cons
from Task.TaskBridgeStargate import TaskBridgeStargate


class AsyncDoTask:
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount

    async def run(self):
        random.shuffle(self.mListAccount)
        await self.BrigdeStargate()

    async def BrigdeStargate(self):
        for i in range(0, len(self.mListAccount)):
            self.mListAccount[i].mAddress = Web3.to_checksum_address(self.mListAccount[i].mAddress)
            l_FilePath = os.getcwd() + Cons.strLoggingPath.format(
                str(self.mListAccount[i].mGroup) + "_" + str(self.mListAccount[i].mAddress))
            try:
                l_ProxyAddress = Cons.g_Data_Proxy[1] if self.mListAccount[i].mGroup not in Cons.g_Data_Proxy else \
                    Cons.g_Data_Proxy[self.mListAccount[i].mGroup]

                l_RPC = await self.GetChainHaveBalance(self.mListAccount[i])
                print(f"{self.mThreadName}: {l_RPC}")

                if l_RPC is not None:
                    l_Web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(l_RPC, request_kwargs={'proxy': l_ProxyAddress,
                                                                                          'timeout': ClientTimeout(
                                                                                              total=6000)}))
                    l_Account = AccountEVM(self.mListAccount[i].mPrivateKey, l_Web3, self.mListAccount[i].mGroup)
                    l_TaskBridgeStargate = TaskBridgeStargate(l_Web3, l_Account)
                    await l_TaskBridgeStargate.DoTask()
                time.sleep(random.randint(1, 10))

            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.BrigdeStargate: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                print(f"{self.mThreadName}: =>")
                traceback.print_exc()

    async def GetChainHaveBalance(self, pWallet: DataWallet):
        l_FilePath = os.getcwd() + Cons.strLoggingPath.format(
            str(pWallet.mGroup) + "_" + str(pWallet.mAddress))
        try:
            # -------------- Proxy -----------------------------------------
            l_ProxyAddress = Cons.g_Data_Proxy[1] if pWallet.mGroup not in Cons.g_Data_Proxy else \
                Cons.g_Data_Proxy[pWallet.mGroup]

            async with aiohttp.ClientSession() as session:
                l_web3_Base = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Cons.RPC.BASE_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
                                                                                              total=6000)}))
                await l_web3_Base.provider.cache_async_session(session=session)
                l_bal_base = await l_web3_Base.eth.get_balance(pWallet.mAddress)

            async with aiohttp.ClientSession() as session:
                l_web3_OP = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Cons.RPC.OP_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
                                                                                              total=6000)}))
                await l_web3_OP.provider.cache_async_session(session=session)
                l_bal_OP = await l_web3_OP.eth.get_balance(pWallet.mAddress)

            async with aiohttp.ClientSession() as session:
                l_web3_Scroll = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Cons.RPC.SCROLL_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
                                                                                              total=6000)}))
                await l_web3_Scroll.provider.cache_async_session(session=session)
                l_bal_Scroll = await l_web3_Scroll.eth.get_balance(pWallet.mAddress)

            async with aiohttp.ClientSession() as session:
                l_web3_arb = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Cons.RPC.ARB_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
                                                                                              total=6000)}))
                await l_web3_arb.provider.cache_async_session(session=session)
                l_bal_arb = await l_web3_arb.eth.get_balance(pWallet.mAddress)

            async with aiohttp.ClientSession() as session:
                l_web3_Linea = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Cons.RPC.LINEA_RPC, request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(
                                                                                              total=6000)}))
                await l_web3_Linea.provider.cache_async_session(session=session)
                l_bal_Linea = await l_web3_Linea.eth.get_balance(pWallet.mAddress)

            l_DictValue = {
                l_web3_Base: l_bal_base,
                l_web3_OP: l_bal_OP,
                l_web3_Scroll: l_bal_Scroll,
                l_web3_Linea: l_bal_Linea,
                l_web3_arb: l_bal_arb,
            }
            l_RPCHasBalance = max(l_DictValue, key=l_DictValue.get)

            if Web3.from_wei(l_DictValue[l_RPCHasBalance], "ether") > 0.005:
                return l_RPCHasBalance.provider.endpoint_uri
        except TimeoutError as t:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.GetChainHaveBalance: TimeoutError\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)
        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.GetChainHaveBalance: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None
