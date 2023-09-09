import hashlib
import logging
import re
import time

from PyQt6.QtCore import pyqtSignal, QRunnable, QObject
from adbutils import AdbDevice

logger = logging.getLogger('root')


class TestCaseSignals(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(dict, Exception)
    result = pyqtSignal(dict, bool)
    started = pyqtSignal(dict)
    show_messagebox = pyqtSignal(str, dict)


class TestCaseRunnable(QRunnable):
    def __init__(self, app, device: AdbDevice, testcase: dict):
        super(TestCaseRunnable, self).__init__()
        self.is_success = False
        self.shell_result = None
        self.signal = TestCaseSignals()
        self.app = app
        self.testcase = testcase
        self.device = device
        self.is_manual_test = testcase['type'] == self.app.tr('手动测试')
        self.expected = testcase.get('expected', None)
        # 用作当前测试的唯一标识
        self.id = hashlib.md5(f'{str(id(self))}_{str(time.time_ns())}'.encode()).hexdigest()[:6]
        self.app.signals.finished.connect(self.terminate)
        self.is_running = True
        logger.debug(f'{self.testcase["name"]} {self.id} is_manual_running {self.is_manual_test}')

    def run(self):
        try:
            self.signal.started.emit(self.testcase)
            if self.is_manual_test:
                self.manual_test()
            else:
                self.automatic_test()
        except Exception as e:
            self.signal.error.emit(self.testcase, e)
        else:
            self.signal.result.emit(self.testcase, self.is_success)
        finally:
            self.stop()
            self.signal.finished.emit(self.testcase)

    def manual_test(self):
        """
        手动测试并等待用户确认
        :return:
        """
        self.signal.show_messagebox.emit(self.id, self.testcase)
        while self.app.message_responses.get(self.id) is None:
            if self.expected:
                stream = self.device.shell(self.testcase['start'], stream=True)
                with stream:
                    f = stream.conn.makefile()
                    while True:
                        if not self.is_running:
                            break
                        line = f.readline()
                        logger.debug(f'line {line}')
                        if self.expected in line:
                            stream.send(b"\003")
                            self.shell_result = line
                            break
                    f.close()
                    break
            else:
                self.device.shell(self.testcase['start'])

        if self.expected:
            self.is_success = self.checked_test_successful()
        else:
            self.is_success = self.app.message_responses.get(self.id, False)

    def automatic_test(self):
        """
        自动测试并判断结果
        :return:
        """
        self.shell_result = self.device.shell(self.testcase['start'])
        self.is_success = self.checked_test_successful()

    def stop(self):
        logger.debug(f'stop {self.testcase["name"]}')
        self.is_manual_test = False
        if self.testcase.get('stop'):
            self.device.shell(self.testcase['stop'])

    def checked_test_successful(self):
        if not self.expected:
            return False
        if self.testcase['key'] in ['usb', 'key-power', 'key-loader']:
            return self.expected in self.shell_result
        elif self.testcase['key'] == 'ethernet':
            loss = re.findall(r'loss=(\d+)', self.shell_result)[0]
            return int(loss) <= int(self.expected)
        else:
            return False

    def terminate(self):
        logger.debug('terminate')
        self.is_running = False
