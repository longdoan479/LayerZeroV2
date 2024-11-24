import os
import random
from datetime import datetime
from symbol import pass_stmt

from web3 import AsyncWeb3

from CONSTANT import strLoggingPath, gDictChainID, ToolBridgeJumper, dead_address
from IncludeAsync.AccountEVM import AccountEVM
from IncludeAsync.Bridge.LayerZero import LayerZero
from IncludeAsync.ConnectWeb3 import ConnectWeb3
from Logging import Logging


class TaskBridgeJumper(ConnectWeb3):
    def __init__(self, pWeb3: AsyncWeb3, pAccountEVM: AccountEVM):
        super().__init__(pWeb3)
        self.mAccountEVM = pAccountEVM

    async def DoTask(self, pRPCTo):
        l_Filepath = os.getcwd() + strLoggingPath.format(str(self.mAccountEVM.mGroup) + "_" + str(self.mAccountEVM.GetAddress()))

        try:
            l_FromChain = gDictChainID[self.mWeb3.provider.endpoint_uri]["chainID"]
            l_ToChain = gDictChainID[pRPCTo]["chainID"]

            l_GasPrice = int(await self.mWeb3.eth.gas_price * random.uniform(1.05, 1.1))
            l_Jumper = LayerZero.Bridge.Jumper(self.mWeb3, l_GasPrice, self.mAccountEVM,   ToolBridgeJumper.Stargate)

            l_QuantityToBridge = (await self.mAccountEVM.GetBalanceETH() - random.uniform(0.0002, 0.0005)) / (random.uniform(1.01, 1.03))

            l_TxnBridge, l_IsSuccessTXN = await l_Jumper.BridgeETH(l_FromChain,
                                                                   l_ToChain,
                                                                   float(round(AsyncWeb3.from_wei(l_QuantityToBridge, "ether"), random.randint(7, 10))),
                                                                   dead_address)
            if l_IsSuccessTXN:
                l_TextToLog = f'\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeJumper - Account {self.mAccountEVM.GetAddress()}:' \
                              f'\n => Bridge from {l_FromChain} to {l_ToChain}\n' \
                              f'\n => {str(l_TxnBridge)}\n'
                Logging.WriteLog(l_Filepath, l_TextToLog)

            else:
                l_TextToLog = f'\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeJumper - Account {self.mAccountEVM.GetAddress()}:' \
                              f'\n => Bridge from {l_FromChain} to {l_ToChain}\n' \
                              f'\n => Failed \n'
                Logging.WriteLog(l_Filepath, l_TextToLog)
            return l_TxnBridge, l_IsSuccessTXN

        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskBridgeJumper.DoTask: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_Filepath, l_TextToLog)
