import os
import random
import threading
import time
import traceback
from datetime import datetime
from typing import List

import requests

import CONSTANT as Cons

from web3 import Web3

from Include.AccountEVM import AccountEVM
from Include.Data import DataWallet
from Logging import Logging
from Task.TaskBridgeStargate import TaskBridgeStargate


class ThreadDoTask(threading.Thread):
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        super(ThreadDoTask, self).__init__()
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount
        self.mDictAccTxnNumber = {}

    def run(self):
        random.shuffle(self.mListAccount)
        self.BrigdeStargate()

    def BrigdeStargate(self):
        for i in range(0, len(self.mListAccount)):
            self.mListAccount[i].mAddress = Web3.to_checksum_address(self.mListAccount[i].mAddress)
            l_FilePath = os.getcwd() + Cons.strLoggingPath.format(
                str(self.mListAccount[i].mGroup) + "_" + str(self.mListAccount[i].mAddress))
            try:
                l_Web3 = self.GetChainHaveBalance(self.mListAccount[i])

                if l_Web3 is not None:
                    l_Account = AccountEVM(self.mListAccount[i].mPrivateKey, l_Web3, self.mListAccount[i].mGroup)
                    l_TaskBridgeStargate = TaskBridgeStargate(l_Web3, l_Account)
                    l_TaskBridgeStargate.DoTask()
                time.sleep(random.randint(1, 10))

            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.BrigdeStargate: {str(e)}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                print(f"{self.mThreadName}: =>")
                traceback.print_exc()

    def GetChainHaveBalance(self, pWallet: DataWallet):
        l_FilePath = os.getcwd() + Cons.strLoggingPath.format(
            str(pWallet.mGroup) + "_" + str(pWallet.mAddress))
        try:
            # -------------- Proxy -----------------------------------------
            l_ProxyAddress = Cons.g_Data_Proxy[1] if pWallet.mGroup not in Cons.g_Data_Proxy else \
                Cons.g_Data_Proxy[pWallet.mGroup]
            http_proxy = {
                "http": l_ProxyAddress,
                "https": l_ProxyAddress
            }

            # Tạo một session với proxy
            session = requests.Session()
            session.proxies.update(http_proxy)

            l_web3_Base = Web3(Web3.HTTPProvider(Cons.RPC.BASE_RPC, session=session))
            l_web3_OP = Web3(Web3.HTTPProvider(Cons.RPC.OP_RPC, session=session))
            l_web3_Scroll = Web3(Web3.HTTPProvider(Cons.RPC.SCROLL_RPC, session=session))
            l_web3_Linea = Web3(Web3.HTTPProvider(Cons.RPC.LINEA_RPC, session=session))
            l_web3_arb = Web3(Web3.HTTPProvider(Cons.RPC.ARB_RPC, session=session))

            l_bal_base = l_web3_Base.eth.get_balance(pWallet.mAddress)
            l_bal_OP = l_web3_OP.eth.get_balance(pWallet.mAddress)
            l_bal_Scroll = l_web3_Scroll.eth.get_balance(pWallet.mAddress)
            l_bal_Linea = l_web3_Linea.eth.get_balance(pWallet.mAddress)
            l_bal_arb = l_web3_arb.eth.get_balance(pWallet.mAddress)

            l_DictValue = {
                l_web3_Base: l_bal_base,
                l_web3_OP: l_bal_OP,
                l_web3_Scroll: l_bal_Scroll,
                l_web3_Linea: l_bal_Linea,
                l_web3_arb: l_bal_arb,
            }
            l_RPCHasBalance = max(l_DictValue, key=l_DictValue.get)

            if Web3.from_wei(l_DictValue[l_RPCHasBalance], "ether") > 0.005:
                return l_RPCHasBalance

        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ThreadDoTask.GetChainHaveBalance: {str(e)}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None
