import logging
import os
import sys
from datetime import datetime

from PyQt6.QtCore import QTimer, QThreadPool, Qt, QTranslator, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QHeaderView

from config import Config
from config.logger import setup_custom_logger
from deviceinfo import DeviceInfo
from main_window import Ui_MainWindow
from util import PyInstallerPathUtil
from test_thread import TestCaseRunnable

# 获取默认的根日志记录器
logger = setup_custom_logger('root')


class MainWindowSignals(QObject):
    finished = pyqtSignal()


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.bundle_dir = PyInstallerPathUtil.get_pyinstaller_base_path()
        os.environ['ADBUTILS_ADB_PATH'] = os.path.join(self.bundle_dir, 'bin')
        self.translator = QTranslator()
        self.logs_folder = None
        self.output_folder = None
        self.is_initialized = False  # 添加初始化状态标志，初始为False
        self.all_tests_successful = True
        self.all_test_result = {}
        self.device_number = None
        self.config = Config()
        self.device = DeviceInfo()
        self.timer = QTimer(self)
        self.message_responses = {}
        self.selected_test_names = []
        self.threadpool_manual = QThreadPool.globalInstance()
        self.threadpool_manual.setMaxThreadCount(1)
        self.threadpool_automatic = QThreadPool()
        self.threadpool_automatic.setMaxThreadCount(8)
        self.signals = MainWindowSignals()
        # 创建一个 QTimer 对象，并连接到更新状态的槽函数
        self.timer.timeout.connect(self.update_device_info)
        # 设置定时器触发时间间隔（以毫秒为单位，这里设置为每秒触发一次）
        self.timer.start(2000)
        self.setupUi(self)
        self.init_ui()
        self.load_language('zh')
        self.update_device_info()

    def change_language_english(self):
        self.load_language('en')

    def change_language_chinese(self):
        self.load_language('zh')

    def load_language(self, language_code):
        # 加载指定语言的翻译文件
        if self.translator.load(os.path.join(self.bundle_dir, f"translations/FactoryTest_{language_code}.qm")):
            QCoreApplication.installTranslator(self.translator)
            self.retranslateUi(self)
            self.config.config_file = f'config/config_{language_code}.yaml'
            self.config.load_config()
            self.load_test_case()

    # noinspection DuplicatedCode
    def init_ui(self):
        # hide camera widget
        self.action_chinese.triggered.connect(self.change_language_chinese)
        self.action_english.triggered.connect(self.change_language_english)
        self.camera_widget.hide()
        self.video_frame.hide()
        self.button_manual_test.hide()
        self.button_add_testcase.clicked.connect(self.button_click_listener)
        self.button_start_test.clicked.connect(self.button_click_listener)
        self.button_test_all.clicked.connect(self.button_click_listener)
        self.button_test_selected.clicked.connect(self.button_click_listener)
        self.button_manual_test.clicked.connect(self.button_click_listener)
        self.button_exit_test.clicked.connect(self.button_click_listener)
        self.button_move_up.clicked.connect(self.button_click_listener)
        self.button_move_down.clicked.connect(self.button_click_listener)
        self.button_remove_testcase.clicked.connect(self.button_click_listener)
        self.button_camera_stream1.clicked.connect(self.button_click_listener)
        self.button_camera_stream2.clicked.connect(self.button_click_listener)
        self.button_camera_stream3.clicked.connect(self.button_click_listener)
        self.button_close_camera.clicked.connect(self.button_click_listener)
        self.button_open_camera.clicked.connect(self.button_click_listener)
        self.button_start_scan.clicked.connect(self.button_click_listener)
        self.button_stop_scan.clicked.connect(self.button_click_listener)
        self.button_switch_camera.clicked.connect(self.button_click_listener)
        self.disable_buttons()

    def load_test_case(self):
        self.listwidget_all_testcase.clear()
        self.listwidget_all_testcase.addItems(self.config.names)
        self.update_current_testcase()

    def update_current_testcase(self):
        logger.debug(f'update current testcase')
        self.tablewidget_testcase.clearContents()
        self.tablewidget_testcase.setRowCount(self.config.size)
        for index, item in enumerate(self.config.currents):
            item['index'] = index
            logger.debug(f'current testCase index {index}, item {item}')
            self.tablewidget_testcase.setItem(index, 0, QTableWidgetItem(item['name']))
            self.tablewidget_testcase.setItem(index, 1, QTableWidgetItem(item['type']))
            self.tablewidget_testcase.setItem(index, 2, QTableWidgetItem('waiting'))
        # 自适应列宽度
        header = self.tablewidget_testcase.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def update_device_info(self):
        self.device.update_devices()
        if self.device_number != self.device.size:
            if self.device.size == 1:
                self.label_device_status.setText(self.tr('ADB 设备已连接'))
                self.update_test_log('device connected')
                self.enable_buttons()  # 一台设备连接时启用按钮
            elif self.device.size > 1:
                self.label_device_status.setText(self.tr('多台ADB设备已连接'))
                self.update_test_log('more than one device connected')
                self.disable_buttons()  # 多台设备连接时禁用按钮
            else:
                self.label_device_status.setText(self.tr('无设备连接'))
                self.disable_buttons()  # 无设备连接时禁用按钮
                self.update_test_log('device disconnected')
                self.cancel_all_testcase()
            self.device_number = self.device.size

    def button_click_listener(self):
        sender_id = self.sender().objectName()
        match sender_id:
            case 'button_start_test':
                self.update_test_log('init factory test')
                self.is_initialized = True
                self.all_tests_successful = True
                self.all_test_result.clear()
                self.enable_buttons()
                self.init_factory_test()
                logger.debug('start test')
            case 'button_test_all':
                logger.debug('test all')
                self.update_test_log('start all test')
                self.cancel_all_testcase()
                # 开启多个线程进行测试
                for item in self.config.currents:
                    self.start_testcase_runnable(item)
            case 'button_test_selected':
                logger.debug('test selected')
                self.update_selected_test_names()
                self.config.update_selected_items(self.selected_test_names)
                for item in self.config.selected_items:
                    self.all_test_result.pop(item['key'])
                    self.start_testcase_runnable(item)
            case 'button_manual_test':
                logger.debug('manual test')
            case 'button_exit_test':
                self.is_initialized = False
                self.update_test_log('exit factory test')
                self.disable_buttons()
                self.cancel_all_testcase()
                logger.debug('exit test')
            case 'button_move_up':
                logger.debug('↑')
                self.move_selected_rows_up()
            case 'button_move_down':
                logger.debug('↓')
                self.move_selected_rows_down()
            case 'button_remove_testcase':
                logger.debug(f'remove test case')
                self.remove_selected_testcase()
            case 'button_add_testcase':
                logger.debug(f'add test case')
                self.add_selected_testcase()
            case _:
                logger.debug(f'{sender_id} To be realized')

    def cancel_all_testcase(self):
        self.update_test_log('cancel all test')

        self.all_test_result.clear()
        self.message_responses.clear()
        # self.threadpool_manual.waitForDone()
        # self.threadpool_automatic.waitForDone()
        self.threadpool_manual.clear()
        self.threadpool_automatic.clear()

    def update_selected_test_names(self):
        self.selected_test_names = [item.text() for item in self.tablewidget_testcase.selectedItems()
                                    if item.column() == 0]

    # noinspection DuplicatedCode
    def start_testcase_runnable(self, item):
        runnable = TestCaseRunnable(self, self.device.device, item)
        runnable.signal.started.connect(self.handle_test_started)
        runnable.signal.error.connect(self.handle_test_error)
        runnable.signal.result.connect(self.handle_test_result)
        runnable.signal.finished.connect(self.handle_test_finished)
        runnable.signal.show_messagebox.connect(self.handle_show_messagebox)
        if runnable.is_manual_test:
            self.threadpool_manual.start(runnable)
        else:
            self.threadpool_automatic.start(runnable)

    def add_selected_testcase(self):
        names = [item.text() for item in self.listwidget_all_testcase.selectedItems()]
        self.config.update_item_status(names=names, enabled=True)
        self.update_current_testcase()

    def remove_selected_testcase(self):
        self.update_selected_test_names()
        self.config.update_item_status(names=self.selected_test_names, enabled=False)
        self.update_current_testcase()

    def move_selected_rows_up(self):
        selected_rows = set()
        for item in self.tablewidget_testcase.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            if row > 0:
                self.swap_rows(row, row - 1)
        self.update_testcase_index()

    def move_selected_rows_down(self):
        selected_rows = set()
        for item in self.tablewidget_testcase.selectedItems():
            selected_rows.add(item.row())

        rows = list(selected_rows)
        rows.sort(reverse=True)

        for row in rows:
            if row < self.tablewidget_testcase.rowCount() - 1:
                self.swap_rows(row, row + 1)
        self.update_testcase_index()

    def swap_rows(self, row1, row2):
        for col in range(self.tablewidget_testcase.columnCount()):
            item1 = self.tablewidget_testcase.takeItem(row1, col)
            item2 = self.tablewidget_testcase.takeItem(row2, col)
            self.tablewidget_testcase.setItem(row1, col, item2)
            self.tablewidget_testcase.setItem(row2, col, item1)

    def update_testcase_index(self):
        # 重新排序配置文件
        name_to_index = {}
        for index in range(self.tablewidget_testcase.rowCount()):
            name = self.tablewidget_testcase.item(index, 0).text()
            if name not in name_to_index:
                name_to_index[name] = index
        for item in self.config.currents:
            name = item['name']
            item['index'] = name_to_index[name]
        self.config.save_config()

    def handle_test_started(self, testcase):
        self.update_test_log(f'{testcase["name"]} start')
        self.tablewidget_testcase.setItem(testcase['index'], 2, QTableWidgetItem('testing'))

    def handle_test_result(self, testcase, success):
        passed = 'pass' if success else 'failed'
        self.update_test_log(f'{testcase["name"]} is {passed}')
        logger.debug(f'testcase {testcase} test result is success {success}')
        result_item = QTableWidgetItem(passed)
        result_item.setForeground(Qt.GlobalColor.white)
        # 绿色 or 红色
        result_item.setBackground(QColor(89, 158, 94) if success else QColor(181, 71, 71))
        self.tablewidget_testcase.setItem(testcase['index'], 2, result_item)
        self.all_test_result[testcase['key']] = passed
        # 更新测试状态
        self.all_tests_successful = all(value == 'pass' for value in self.all_test_result.values())

    def handle_show_messagebox(self, runnable_id, testcase):
        logger.debug(f'handle_show_messagebox {testcase}')
        if testcase.get('expected'):
            reply = QMessageBox.information(self, testcase.get('name'), testcase.get('tips'))
        else:
            reply = QMessageBox.question(self, testcase.get('name'), testcase.get('tips'),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.message_responses[runnable_id] = reply == QMessageBox.StandardButton.Yes

    def handle_test_finished(self, testcase):
        logger.debug('handle_test_finished')
        self.update_test_log(f'{testcase["name"]} finish')
        self.check_all_tests_complete()  # 在测试完成时检查所有测试是否完成

    def handle_test_error(self, testcase, error):
        logger.error(error)
        self.update_test_log(f'{testcase["name"]} error')

    def update_test_log(self, message):
        self.listwidget_log.insertItem(0, message)

    def disable_buttons(self):
        # 禁用需要禁用的按钮
        self.button_test_all.setDisabled(True)
        self.button_test_selected.setDisabled(True)
        self.button_manual_test.setDisabled(True)
        self.button_exit_test.setDisabled(True)
        self.signals.finished.emit()
        for index, _ in enumerate(self.config.currents):
            self.tablewidget_testcase.setItem(index, 2, QTableWidgetItem('waiting'))

    def enable_buttons(self):
        # 启用需要启用的按钮
        if not self.is_initialized:
            return

        if not self.device_number == 1:
            QMessageBox.warning(self, self.tr('设备断开连接'), self.tr('设备已断开连接，请重新连接设备'))
            return

        self.button_test_all.setDisabled(False)
        self.button_test_selected.setDisabled(False)
        self.button_manual_test.setDisabled(False)
        self.button_exit_test.setDisabled(False)

    def check_all_tests_complete(self):
        logger.debug(f'check_all_tests_complete {self.all_test_result}')
        # logger.debug(f'{self.all_test_result} {set(self.all_test_result.keys())} == {set(self.config.keys)}')
        if set(self.all_test_result.keys()) == set(self.config.keys):
            # 所有测试已完成，检查测试状态
            if self.all_tests_successful:
                self.update_test_log("All tests completed successfully.")
                QMessageBox.information(self, self.tr('测试结束'), self.tr('测试成功'))
            else:
                self.update_test_log("Some tests failed.")
                # 可以在这里执行失败时的操作，例如显示警告或弹出消息框
                QMessageBox.warning(self, self.tr('测试结束'), self.tr('部分测试项目失败'))

            self.device.save_device_info(self.all_test_result, self.all_tests_successful)

    def init_factory_test(self):

        # 检查output文件夹是否存在，如果不存在则创建
        self.output_folder = 'output'
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # 检查logs文件夹是否存在，如果不存在则创建
        self.logs_folder = 'logs'
        if not os.path.exists(self.logs_folder):
            os.makedirs(self.logs_folder)

        if not self.device_number == 1:
            return
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        log_filename = f'{self.device.device_info["SN"]}_{current_time}.log'
        log_filepath = os.path.join(self.logs_folder, log_filename)

        # 创建一个FileHandler，初始时不设置文件名
        file_handler = logging.FileHandler(filename=log_filepath, mode='a', encoding='UTF-8')  # 'a'表示追加日志到文件
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        # 设置日志级别和格式
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        # 添加FileHandler到日志记录器
        logger.addHandler(file_handler)

    def closeEvent(self, event):
        logger.debug(f'close app {self.threadpool_manual.activeThreadCount()}')
        self.signals.finished.emit()
        self.cancel_all_testcase()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
