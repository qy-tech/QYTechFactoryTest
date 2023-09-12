import threading

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QEventLoop


class Toast(QtWidgets.QFrame):
    # 信号，用于在通知关闭时发射
    closed = QtCore.pyqtSignal()

    # 类级别属性，用于存储当前显示的 Toast 实例
    current_toast = None

    # 锁，用于确保只有一个线程能够显示 Toast
    toast_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super(Toast, self).__init__(*args, **kwargs)
        QtWidgets.QHBoxLayout(self)

        # 设置大小策略
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,
                           QtWidgets.QSizePolicy.Policy.Maximum)

        # 设置样式表
        self.setStyleSheet('''
            Toast {
                border: 1px solid black;
                border-radius: 4px; 
                background: palette(window);
            }
        ''')

        # 创建定时器，用于自动隐藏通知
        self.timer = QtCore.QTimer(singleShot=True)
        self.timer.timeout.connect(self.hide)
        self.event_loop = QEventLoop()
        # 根据是否有父部件选择不同的动画方式
        if self.parentWidget():
            # 如果有父部件，使用 QGraphicsOpacityEffect 实现渐变效果
            self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
            self.setGraphicsEffect(self.opacity_effect)
            self.opacity_ani = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
            self.parentWidget().installEventFilter(self)
        else:
            # 如果没有父部件，使用窗口透明度实现渐变效果
            self.opacity_ani = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.opacity_ani.setStartValue(0.)
        self.opacity_ani.setEndValue(1.)
        self.opacity_ani.setDuration(100)
        self.opacity_ani.finished.connect(self.check_closed)

        # 通知显示的位置和边距
        self.corner = QtCore.Qt.Corner.TopLeftCorner
        self.margin = 10

    def check_closed(self):
        # 检查通知是否已关闭
        if self.opacity_ani.direction() == QtCore.QAbstractAnimation.Direction.Backward:
            self.close()

            # 发射通知关闭信号
            self.closed.emit()

            # 将当前显示的 Toast 实例设置为 None
            with Toast.toast_lock:
                Toast.current_toast = None

    def restore(self):
        # 还原通知的状态，停止定时器和渐变动画
        self.timer.stop()
        self.opacity_ani.stop()
        if self.parentWidget():
            self.opacity_effect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # 隐藏通知，启动渐变动画
        self.event_loop.quit()
        self.opacity_ani.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.opacity_ani.setDuration(500)
        self.opacity_ani.start()

    def event_filter(self, source, event):
        # 事件过滤器，用于处理父部件的大小变化事件
        if source == self.parentWidget() and event.type() == QtCore.QEvent.Type.Resize:
            self.opacity_ani.stop()
            parent_rect = self.parentWidget().rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.Corner.TopLeftCorner:
                geo.moveTopLeft(
                    parent_rect.topLeft() + QtCore.QPoint(self.margin, self.margin))
            elif self.corner == QtCore.Qt.Corner.TopRightCorner:
                geo.moveTopRight(
                    parent_rect.topRight() + QtCore.QPoint(-self.margin, self.margin))
            elif self.corner == QtCore.Qt.Corner.BottomRightCorner:
                geo.moveBottomRight(
                    parent_rect.bottomRight() + QtCore.QPoint(-self.margin, -self.margin))
            else:
                geo.moveBottomLeft(
                    parent_rect.bottomLeft() + QtCore.QPoint(self.margin, -self.margin))
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(Toast, self).event_filter(source, event)

    def enter_event(self, event):
        # 鼠标进入通知时，取消定时器，保持通知可见
        self.restore()

    def leave_event(self, event):
        # 鼠标离开通知时，重新启动定时器，用于自动隐藏通知
        self.timer.start()

    def close_event(self, event):
        # 通知关闭时的处理，删除通知
        self.deleteLater()

    def resize_event(self, event):
        # 处理通知窗口的大小变化事件
        super(Toast, self).resize_event(event)
        if not self.parentWidget():
            # 如果没有父部件，设置通知窗口的形状为圆角矩形
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()).translated(-.5, -.5), 4, 4)
            self.setMask(QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon()))
        else:
            # 如果有父部件，清除通知窗口的形状
            self.clearMask()

    @staticmethod
    def show_message(parent, message,
                     icon=QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation,
                     corner=None, margin=10, closable=True,
                     timeout=3000, desktop=False, parent_window=True):
        if parent and parent_window:
            parent = parent.window()

        if not parent or desktop:
            # 创建 Toaster 通知窗口，用于在桌面上显示通知
            self = Toast(None)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint |
                                QtCore.Qt.WindowType.BypassWindowManagerHint)
            self.__self = self

            current_screen = QtWidgets.QApplication.primaryScreen()
            if parent and parent.window().geometry().size().isValid():
                reference = parent.window().geometry()
            else:
                reference = QtCore.QRect(
                    QtGui.QCursor.pos() - QtCore.QPoint(1, 1),
                    QtCore.QSize(3, 3))
            max_area = 0
            for screen in QtWidgets.QApplication.screens():
                intersected = screen.geometry().intersected(reference)
                area = intersected.width() * intersected.height()
                if area > max_area:
                    max_area = area
                    current_screen = screen
            parent_rect = current_screen.availableGeometry()
        else:
            # 创建 Toaster 通知窗口，用于在指定父部件上显示通知
            self = Toast(parent)
            parent_rect = parent.rect()

        self.timer.setInterval(timeout)

        if isinstance(icon, QtWidgets.QStyle.StandardPixmap):
            label_icon = QtWidgets.QLabel()
            self.layout().addWidget(label_icon)
            icon = self.style().standardIcon(icon)
            size = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)
            label_icon.setPixmap(icon.pixmap(size))

        self.label = QtWidgets.QLabel(message)
        self.layout().addWidget(self.label)

        if closable:
            self.close_button = QtWidgets.QToolButton()
            self.layout().addWidget(self.close_button)
            close_icon = self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton)
            self.close_button.setIcon(close_icon)
            self.close_button.setAutoRaise(True)
            self.close_button.clicked.connect(self.close)

        self.raise_()
        self.adjustSize()

        self.corner = corner
        self.margin = margin

        geo = self.geometry()
        if corner == QtCore.Qt.Corner.TopLeftCorner:
            geo.moveTopLeft(
                parent_rect.topLeft() + QtCore.QPoint(margin, margin))
        elif corner == QtCore.Qt.Corner.TopRightCorner:
            geo.moveTopRight(
                parent_rect.topRight() + QtCore.QPoint(-margin, margin))
        elif corner == QtCore.Qt.Corner.BottomRightCorner:
            geo.moveBottomRight(
                parent_rect.bottomRight() + QtCore.QPoint(-margin, -margin))
        elif corner == QtCore.Qt.Corner.BottomLeftCorner:
            geo.moveBottomLeft(
                parent_rect.bottomLeft() + QtCore.QPoint(margin, -margin))
        else:
            geo.moveCenter(parent_rect.center())
        self.setGeometry(geo)
        self.show()
        self.opacity_ani.start()
        self.timer.start()
        self.event_loop.exec()
        # 将当前显示的 Toast 实例设置为 self
        with Toast.toast_lock:
            Toast.current_toast = self
