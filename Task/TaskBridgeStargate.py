import os
import random
import time
from datetime import datetime

import requests
from aiohttp import ClientTimeout
from web3 import Web3, AsyncWeb3

from IncludeAsync.AccountEVM import AccountEVM
from IncludeAsync.Bridge.LayerZero import LayerZero
from IncludeAsync.ConnectWeb3 import ConnectWeb3
import CONSTANT as Cons
from Logging import Logging


class TaskBridgeStargate(ConnectWeb3):
    def __init__(self, pWeb3: AsyncWeb3, pAccountEVM: AccountEVM):
        super().__init__(pWeb3)
        self.mAccountEVM = pAccountEVM

    async def DoTask(self):
        l_FilePath = os.getcwd() + Cons.strLoggingPath.format(
            str(self.mAccountEVM.mGroup) + "_" + str(self.mAccountEVM.GetAddress()))

        try:
            l_RoutePath = [
                Cons.RPC.OP_RPC,
                Cons.RPC.ARB_RPC,
                Cons.RPC.SCROLL_RPC,
                Cons.RPC.LINEA_RPC,
                Cons.RPC.BASE_RPC,
            ]

            l_RandomAmountRpc = random.randint(3, 4)
            l_RoutePath = [l_rpc for l_rpc in l_RoutePath if l_rpc != self.mWeb3.provider.endpoint_uri][:l_RandomAmountRpc]
            random.shuffle(l_RoutePath)

            for i in range(0, len(l_RoutePath)):
                l_FromChain = Cons.LayerZero_json["ChainInfo"][self.mWeb3.provider.endpoint_uri]["name"]
                l_ToChain = Cons.LayerZero_json["ChainInfo"][l_RoutePath[i]]["name"]
                # -------------- Proxy -----------------------------------------
                l_ProxyAddress = Cons.g_Data_Proxy[1] if self.mAccountEVM.mGroup not in Cons.g_Data_Proxy else \
                    Cons.g_Data_Proxy[self.mAccountEVM.mGroup]
                http_proxy = {
                    "http": l_ProxyAddress,
                    "https": l_ProxyAddress
                }

                # Tạo một session với proxy
                session = requests.Session()
                session.proxies.update(http_proxy)

                l_GasPrice = int(await self.mWeb3.eth.gas_price*random.uniform(1.05, 1.1))

                l_QuantityToBridge = (await self.mAccountEVM.GetBalanceETH() - random.uniform(0.0002, 0.0005)) / (random.uniform(1.01, 1.03))
                l_Stargate = LayerZero.Bridge.StargateBridge(self.mWeb3, l_GasPrice, 0)

                l_TxnBridge, l_IsSuccessTXN = await l_Stargate.BridgeETH(self.mAccountEVM,
                                                   Cons.LayerZero_json["ChainInfo"][l_RoutePath[i]]["chainID"],
                                                   float(round(Web3.from_wei(l_QuantityToBridge, "ether"), random.randint(7, 10))))
                if l_IsSuccessTXN:
                    l_NextChain = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(l_RoutePath[i], request_kwargs={'proxy': l_ProxyAddress, 'timeout': ClientTimeout(total=6000)}))

                    self.mAccountEVM.mWeb3 = l_NextChain
                    self.mWeb3 = l_NextChain

                    l_IsBridgeSucess = await self.IsBridgeSucess(l_QuantityToBridge)
                    if l_IsBridgeSucess:
                        l_TextToLog = f'\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeStargate - Account {self.mAccountEVM.GetAddress()}:' \
                                      f'\n => Bridge from {l_FromChain} to {l_ToChain}\n' \
                                      f'\n => {str(l_TxnBridge)}\n'
                        Logging.WriteLog(l_FilePath, l_TextToLog)
                    else:
                        l_TextToLog = f'\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeStargate - Account {self.mAccountEVM.GetAddress()}:' \
                                      f'\n => Bridge from {l_FromChain} to {l_ToChain}\n' \
                                      f'\n => Failed, "From" is sent but "To" not receive \n'
                        Logging.WriteLog(l_FilePath, l_TextToLog)
                        break
                else:
                    l_TextToLog = f'\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeStargate - Account {self.mAccountEVM.GetAddress()}:' \
                                  f'\n => Bridge from {l_FromChain} to {l_ToChain}\n' \
                                  f'\n => Failed \n'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                    break
            time.sleep(random.randint(1, 10))
        except TimeoutError as t:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeStargate: TimeoutError\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)
        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeStargate: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

    async def IsBridgeSucess(self, pQuantityBridge):
        l_RetryTime = 0
        while l_RetryTime < 120:
            l_Balance = await self.mAccountEVM.GetBalanceETH()
            if int(pQuantityBridge/1.1) <= l_Balance:  # if balance > pQuantityBridge +- 10%
                return True
            else:
                l_RetryTime = l_RetryTime + 1
                time.sleep(10)

        return False