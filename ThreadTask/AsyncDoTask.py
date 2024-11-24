import asyncio
import os
import random
import time
import traceback
from datetime import datetime

import aiohttp
from aiohttp import ClientTimeout
from typing_extensions import List
from web3 import Web3, AsyncWeb3

from CONSTANT import RPC, strLoggingPath, g_ProxyAddress
from Include.Data import DataWallet
from IncludeAsync.AccountEVM import AccountEVM
from Logging import Logging
from Task.TaskBridgeJumper import TaskBridgeJumper
from Task.TaskBridgeStargate import TaskBridgeStargate


class AsyncDoTask:
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount
        self.mDictAccTxnNumber = {}
    async def run(self):
        random.shuffle(self.mListAccount)
        await self.BrigdeStargate()

    async def BrigdeStargate(self):
        l_IsAllAccReachTarget = False
        while not l_IsAllAccReachTarget:
            for i in range(0, len(self.mListAccount)):
                self.mListAccount[i].mAddress = Web3.to_checksum_address(self.mListAccount[i].mAddress)
                l_FilePath = os.getcwd() + strLoggingPath.format(
                    str(self.mListAccount[i].mGroup) + "_" + str(self.mListAccount[i].mAddress))
                try:
                    l_RPC_From = await self.GetChainHaveBalance(self.mListAccount[i])
                    print(f"{self.mThreadName}: Wallet {self.mListAccount[i].mAddress}, RPC {l_RPC_From}")

                    if self.mListAccount[i].mAddress not in self.mDictAccTxnNumber:
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress] = {}
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["TargetTxnAmount"] = random.randint(10, 15)
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["CurrentTxnAmount"] = 0
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["IsDone"] = False
                    else:
                        if self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["IsDone"]:
                            continue

                    if l_RPC_From is None:
                        continue
                    elif l_RPC_From != "":
                        l_RoutePath = [
                            RPC.OP_RPC,
                            RPC.ARB_RPC,
                            RPC.SCROLL_RPC,
                            RPC.LINEA_RPC,
                            RPC.BASE_RPC,
                        ]
                        l_RoutePath = [l_rpc for l_rpc in l_RoutePath if l_rpc != l_RPC_From]
                        l_RPC_To = random.choice(l_RoutePath)
                        async with aiohttp.ClientSession() as session:
                            l_Web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(l_RPC_From, request_kwargs={'proxy': g_ProxyAddress}))
                            await l_Web3.provider.cache_async_session(session=session)
                            l_Account = AccountEVM(self.mListAccount[i].mPrivateKey, l_Web3, self.mListAccount[i].mGroup)

                            l_RandomeRate = random.randint(0, 100)

                            if l_RandomeRate < 0:
                                l_TaskBridgeStargate = TaskBridgeStargate(l_Web3, l_Account)
                                l_TxnBridge, l_IsSuccessTXN = await l_TaskBridgeStargate.DoTask(l_RPC_To)
                            else:
                                l_TaskBridgeJumper = TaskBridgeJumper(l_Web3, l_Account)
                                l_TxnBridge, l_IsSuccessTXN = await l_TaskBridgeJumper.DoTask(l_RPC_To)

                            if l_IsSuccessTXN:
                                self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["CurrentTxnAmount"] += 1
                    else:
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["IsDone"] = True

                    if self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["CurrentTxnAmount"] \
                        >= self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["TargetTxnAmount"]:
                        self.mDictAccTxnNumber[self.mListAccount[i].mAddress]["IsDone"] = True
                    l_IsAllAccReachTarget = all(wallet["IsDone"] == True for wallet in self.mDictAccTxnNumber.values())
                    await asyncio.sleep(random.randint(20, 60))


                except Exception as e:
                    l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.BrigdeStargate: {type(e).__name__} - {e}\n\n'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                    print(f"{self.mThreadName}: =>")
                    traceback.print_exc()

            l_RandomSleep = random.randint(900, 1800)
            print(f"{self.mThreadName}: => Sleeping for {l_RandomSleep}s before next round")
            await asyncio.sleep(l_RandomSleep)
            random.shuffle(self.mListAccount)

    async def GetChainHaveBalance(self, pWallet: DataWallet):
        l_FilePath = os.getcwd() + strLoggingPath.format(
            str(pWallet.mGroup) + "_" + str(pWallet.mAddress))
        try:
            # -------------- Proxy -----------------------------------------

            async with aiohttp.ClientSession() as session:
                l_web3_Base = AsyncWeb3(
                    AsyncWeb3.AsyncHTTPProvider(RPC.BASE_RPC, request_kwargs={'proxy': g_ProxyAddress}))
                await l_web3_Base.provider.cache_async_session(session=session)
                l_bal_base = await l_web3_Base.eth.get_balance(pWallet.mAddress)

                l_web3_OP = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC.OP_RPC, request_kwargs={'proxy': g_ProxyAddress}))
                await l_web3_OP.provider.cache_async_session(session=session)
                l_bal_OP = await l_web3_OP.eth.get_balance(pWallet.mAddress)

                l_web3_Scroll = AsyncWeb3(
                    AsyncWeb3.AsyncHTTPProvider(RPC.SCROLL_RPC, request_kwargs={'proxy': g_ProxyAddress}))
                await l_web3_Scroll.provider.cache_async_session(session=session)
                l_bal_Scroll = await l_web3_Scroll.eth.get_balance(pWallet.mAddress)

                l_web3_arb = AsyncWeb3(
                    AsyncWeb3.AsyncHTTPProvider(RPC.ARB_RPC, request_kwargs={'proxy': g_ProxyAddress}))
                await l_web3_arb.provider.cache_async_session(session=session)
                l_bal_arb = await l_web3_arb.eth.get_balance(pWallet.mAddress)

                l_web3_Linea = AsyncWeb3(
                    AsyncWeb3.AsyncHTTPProvider(RPC.LINEA_RPC, request_kwargs={'proxy': g_ProxyAddress}))
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
                else:
                    return ""
        except TimeoutError as t:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.GetChainHaveBalance: TimeoutError\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)
        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.GetChainHaveBalance: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None
