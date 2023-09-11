import logging
import re
import statistics
import time
import typing
from hashlib import md5

from PyQt6.QtCore import QObject, QProcess, pyqtSignal

from util import Adb

logger = logging.getLogger('root')


class TestCaseProcess(QObject):
    started = pyqtSignal(dict)
    finished = pyqtSignal(dict, bool)
    show_messagebox = pyqtSignal(str, dict)

    def __init__(self, testcase: dict):
        """
        初始化测试项目程序
        :param testcase: 当前的测试项目
        """
        super().__init__()
        self.testcase = testcase
        self.name = self.testcase.get('key')  # 测试用例名称
        self.expected = self.testcase.get('expected')  # 预期结果
        self.is_manual = self.testcase.get('type') == 'manual'  # 是否是手动测试
        self.is_running = False  # 测试是否运行中
        self.is_success = False  # 测试是否成功
        self.output = ''  # 测试输出
        self.uuid = md5(f'{str(id(self))}_{str(time.time_ns())}'.encode()).hexdigest()[:6]  # 生成唯一标识符
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handler_update_output)
        self.process.started.connect(self._handler_on_started)
        self.process.finished.connect(self._handler_on_finished)
        self.process.stateChanged.connect(self._handler_state_changed)

    def start(self):
        """
        开始测试项
        :return:
        """
        try:
            self._start_testcase()
        except Exception as e:
            logger.error(e)

    def terminate(self):
        """
        停止当前正在运行的程序
        :return: None
        """
        self.is_running = False
        self.process.terminate()
        self.process.close()

    def _handler_update_output(self):
        """
        更新程序运行的输出
        :return: None
        """
        self.output = str(self.process.readAllStandardOutput(), 'utf-8')  # 更新测试输出
        logger.debug(f'update process output:\n {self.output}')
        self._wait_for_finished()

    def _handler_on_started(self):
        """
        当前程序运行开始时调用
        :return: None
        """
        self.started.emit(self.testcase)  # 发送测试开始信号
        logger.debug(f'process {self.name} started , expected {self.expected}')

    def _handler_on_finished(self):
        """
        当前程序运行结束时调用
        :return: None
        """
        self.finished.emit(self.testcase, self.is_success)  # 发送测试完成信号
        logger.debug(f'process {self.name} finish')

        if self.testcase.get('stop'):
            Adb.shell(self.testcase['stop'])  # 如果需要停止操作，执行停止命令

    def _handler_state_changed(self):
        """
        当前程序运行状态改变时调用
        :return: None
        """
        if self.process.finished:
            self.is_running = False
            return
        self.is_running = self.process.state() == QProcess.ProcessState.Running  # 更新测试状态
        logger.debug(f'process state is running {self.is_running}')

    def _start_testcase(self):
        """
        启动测试用例的方法。

        根据测试用例的类型，决定是否需要等待用户确认，然后启动测试。
        :return:
        """
        # 根据是否是手动测试和是否有期望值来决定启动流程
        if self.is_manual:
            if self.expected:
                # 弹出消息框等待用户确认，然后启动测试
                self.show_messagebox.emit(self.uuid, self.testcase)
                self.process.start(Adb.adb_path, ['shell', self.testcase['start']])
            else:
                # 先启动测试，然后弹出消息框等待用户确认
                self.process.start(Adb.adb_path, ['shell', self.testcase['start']])
                self.show_messagebox.emit(self.uuid, self.testcase)
        else:
            # 自动测试，直接启动测试
            self.process.start(Adb.adb_path, ['shell', self.testcase['start']])

    def _wait_for_finished(self):
        """
        停止测试用例的方法。

        根据测试用例的类型，决定是否需要等待用户确认，然后设置测试结果。
        :return: None
        """
        if self.is_manual:
            if self.expected:
                self._checked_test_successful()
                logger.debug(f'{self.name} is success {self.is_success}')
            elif TestCaseProcessManager.uuid_manager.get(self.uuid) is not None:
                # 用户确认后设置测试结果
                self.is_success = TestCaseProcessManager.uuid_manager.get(self.uuid)
                logger.debug(f'user confirm {self.name} is success {self.is_success}')
                self.terminate()
        else:
            self._checked_test_successful()
            logger.debug(f'{self.name} is success {self.is_success}')

    def _checked_test_successful(self):
        """
        根据测试用例的类型和输出来判断测试是否成功
        :return: None
        """
        if self.testcase['key'] in ['usb', 'key-power', 'key-loader']:
            self.is_success = self.expected in self.output
        elif self.testcase['key'] == 'ethernet':
            loss = re.findall(r'loss=(\d+)', self.output)
            if loss:
                self.is_success = int(loss[0]) <= int(self.expected)
        else:
            self.is_success = False

        if self.is_success:
            self.terminate()


class TestCaseProcessManager(QObject):
    uuid_manager = {}
    automated_processes: typing.List[TestCaseProcess] = []
    manual_processes: typing.List[TestCaseProcess] = []

    @staticmethod
    def clear():
        for process in TestCaseProcessManager.automated_processes:
            process.terminate()

        for process in TestCaseProcessManager.manual_processes:
            process.terminate()

        TestCaseProcessManager.uuid_manager.clear()
        TestCaseProcessManager.automated_processes.clear()
        TestCaseProcessManager.manual_processes.clear()

    @staticmethod
    def start_testcase_process():
        for process in TestCaseProcessManager.automated_processes:
            process.start()
        for process in TestCaseProcessManager.manual_processes:
            process.start()
