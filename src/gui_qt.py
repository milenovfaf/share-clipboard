
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QStyle, qApp
import app_settings
import logging

log = logging.getLogger(__name__)


# qt http://qtdocs.narod.ru/4.1.0/doc/html/qwidget.html#minimized-prop


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(501, 404)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(501, 404))
        MainWindow.setMaximumSize(QtCore.QSize(501, 404))
        MainWindow.setAcceptDrops(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.ip = QtWidgets.QLineEdit(self.centralwidget)
        self.ip.setGeometry(QtCore.QRect(16, 40, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip.sizePolicy().hasHeightForWidth())
        self.ip.setSizePolicy(sizePolicy)
        self.ip.setStyleSheet("font-size: 10pt;")
        self.ip.setText("")
        self.ip.setMaxLength(20)
        self.ip.setClearButtonEnabled(False)
        self.ip.setObjectName("ip")
        self.port = QtWidgets.QLineEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(175, 40, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.port.sizePolicy().hasHeightForWidth())
        self.port.setSizePolicy(sizePolicy)
        self.port.setStyleSheet("font-size: 10pt;")
        self.port.setMaxLength(5)
        self.port.setObjectName("port")
        self.label_ip = QtWidgets.QLabel(self.centralwidget)
        self.label_ip.setGeometry(QtCore.QRect(21, 10, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_ip.sizePolicy().hasHeightForWidth())
        self.label_ip.setSizePolicy(sizePolicy)
        self.label_ip.setBaseSize(QtCore.QSize(0, 0))
        self.label_ip.setStyleSheet("font-size: 12pt;")
        self.label_ip.setScaledContents(False)
        self.label_ip.setObjectName("label_ip")
        self.button_apply = QtWidgets.QPushButton(self.centralwidget)
        self.button_apply.setGeometry(QtCore.QRect(176, 341, 151, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_apply.sizePolicy().hasHeightForWidth())
        self.button_apply.setSizePolicy(sizePolicy)
        self.button_apply.setStyleSheet("font-size: 12pt;")
        self.button_apply.setObjectName("button_apply")
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QtCore.QRect(178, 10, 91, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_port.sizePolicy().hasHeightForWidth())
        self.label_port.setSizePolicy(sizePolicy)
        self.label_port.setBaseSize(QtCore.QSize(0, 0))
        self.label_port.setStyleSheet("font-size: 12pt;")
        self.label_port.setScaledContents(False)
        self.label_port.setObjectName("label_port")
        self.copy_join_keys = QtWidgets.QLineEdit(self.centralwidget)
        self.copy_join_keys.setGeometry(QtCore.QRect(17, 200, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.copy_join_keys.sizePolicy().hasHeightForWidth())
        self.copy_join_keys.setSizePolicy(sizePolicy)
        self.copy_join_keys.setStyleSheet("font-size: 10pt;")
        self.copy_join_keys.setMaxLength(30)
        self.copy_join_keys.setObjectName("copy_join_keys")
        self.label_copy_join_keys = QtWidgets.QLabel(self.centralwidget)
        self.label_copy_join_keys.setGeometry(QtCore.QRect(22, 170, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_copy_join_keys.sizePolicy().hasHeightForWidth())
        self.label_copy_join_keys.setSizePolicy(sizePolicy)
        self.label_copy_join_keys.setBaseSize(QtCore.QSize(0, 0))
        self.label_copy_join_keys.setMouseTracking(True)
        self.label_copy_join_keys.setStyleSheet("font-size: 12pt;")
        self.label_copy_join_keys.setScaledContents(False)
        self.label_copy_join_keys.setObjectName("label_copy_join_keys")
        self.copy_share_keys = QtWidgets.QLineEdit(self.centralwidget)
        self.copy_share_keys.setGeometry(QtCore.QRect(176, 200, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.copy_share_keys.sizePolicy().hasHeightForWidth())
        self.copy_share_keys.setSizePolicy(sizePolicy)
        self.copy_share_keys.setStyleSheet("font-size: 10pt;")
        self.copy_share_keys.setMaxLength(30)
        self.copy_share_keys.setObjectName("copy_share_keys")
        self.label_copy_share_keys = QtWidgets.QLabel(self.centralwidget)
        self.label_copy_share_keys.setGeometry(QtCore.QRect(182, 171, 131, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_copy_share_keys.sizePolicy().hasHeightForWidth())
        self.label_copy_share_keys.setSizePolicy(sizePolicy)
        self.label_copy_share_keys.setBaseSize(QtCore.QSize(0, 0))
        self.label_copy_share_keys.setStyleSheet("font-size: 12pt;")
        self.label_copy_share_keys.setScaledContents(False)
        self.label_copy_share_keys.setObjectName("label_copy_share_keys")
        self.label_error = QtWidgets.QLabel(self.centralwidget)
        self.label_error.setGeometry(QtCore.QRect(20, 310, 461, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_error.sizePolicy().hasHeightForWidth())
        self.label_error.setSizePolicy(sizePolicy)
        self.label_error.setBaseSize(QtCore.QSize(0, 0))
        self.label_error.setStyleSheet("font-size: 12pt;\n"
                                       "color: #FF0000;\n"
                                       "text-align: center;")
        self.label_error.setScaledContents(False)
        self.label_error.setAlignment(QtCore.Qt.AlignCenter)
        self.label_error.setObjectName("label_error")
        self.client_name = QtWidgets.QLineEdit(self.centralwidget)
        self.client_name.setGeometry(QtCore.QRect(334, 40, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.client_name.sizePolicy().hasHeightForWidth())
        self.client_name.setSizePolicy(sizePolicy)
        self.client_name.setStyleSheet("font-size: 10pt;")
        self.client_name.setText("")
        self.client_name.setMaxLength(30)
        self.client_name.setClearButtonEnabled(False)
        self.client_name.setObjectName("client_name")
        self.label_client_name = QtWidgets.QLabel(self.centralwidget)
        self.label_client_name.setGeometry(QtCore.QRect(340, 11, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_client_name.sizePolicy().hasHeightForWidth())
        self.label_client_name.setSizePolicy(sizePolicy)
        self.label_client_name.setBaseSize(QtCore.QSize(0, 0))
        self.label_client_name.setStyleSheet("font-size: 12pt;")
        self.label_client_name.setScaledContents(False)
        self.label_client_name.setObjectName("label_client_name")
        self.label_client_name_for_sync = QtWidgets.QLabel(self.centralwidget)
        self.label_client_name_for_sync.setGeometry(
            QtCore.QRect(23, 90, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_client_name_for_sync.sizePolicy().hasHeightForWidth())
        self.label_client_name_for_sync.setSizePolicy(sizePolicy)
        self.label_client_name_for_sync.setBaseSize(QtCore.QSize(0, 0))
        self.label_client_name_for_sync.setStyleSheet("font-size: 12pt;")
        self.label_client_name_for_sync.setScaledContents(False)
        self.label_client_name_for_sync.setObjectName(
            "label_client_name_for_sync")
        self.client_name_for_sync = QtWidgets.QLineEdit(self.centralwidget)
        self.client_name_for_sync.setGeometry(QtCore.QRect(17, 120, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.client_name_for_sync.sizePolicy().hasHeightForWidth())
        self.client_name_for_sync.setSizePolicy(sizePolicy)
        self.client_name_for_sync.setStyleSheet("font-size: 10pt;")
        self.client_name_for_sync.setText("")
        self.client_name_for_sync.setMaxLength(30)
        self.client_name_for_sync.setClearButtonEnabled(False)
        self.client_name_for_sync.setObjectName("client_name_for_sync")
        self.connector_enter_keys = QtWidgets.QLineEdit(self.centralwidget)
        self.connector_enter_keys.setGeometry(QtCore.QRect(18, 270, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.connector_enter_keys.sizePolicy().hasHeightForWidth())
        self.connector_enter_keys.setSizePolicy(sizePolicy)
        self.connector_enter_keys.setStyleSheet("font-size: 10pt;")
        self.connector_enter_keys.setMaxLength(30)
        self.connector_enter_keys.setObjectName("connector_enter_keys")
        self.label_connector_enter_keys = QtWidgets.QLabel(self.centralwidget)
        self.label_connector_enter_keys.setGeometry(
            QtCore.QRect(24, 240, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_connector_enter_keys.sizePolicy().hasHeightForWidth())
        self.label_connector_enter_keys.setSizePolicy(sizePolicy)
        self.label_connector_enter_keys.setBaseSize(QtCore.QSize(0, 0))
        self.label_connector_enter_keys.setStyleSheet("font-size: 12pt;")
        self.label_connector_enter_keys.setScaledContents(False)
        self.label_connector_enter_keys.setObjectName(
            "label_connector_enter_keys")
        self.label_connector_space_bar_keys = QtWidgets.QLabel(
            self.centralwidget)
        self.label_connector_space_bar_keys.setGeometry(
            QtCore.QRect(181, 240, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_connector_space_bar_keys.sizePolicy().hasHeightForWidth())
        self.label_connector_space_bar_keys.setSizePolicy(sizePolicy)
        self.label_connector_space_bar_keys.setBaseSize(QtCore.QSize(0, 0))
        self.label_connector_space_bar_keys.setStyleSheet("font-size: 12pt;")
        self.label_connector_space_bar_keys.setScaledContents(False)
        self.label_connector_space_bar_keys.setObjectName(
            "label_connector_space_bar_keys")
        self.connector_space_bar_keys = QtWidgets.QLineEdit(self.centralwidget)
        self.connector_space_bar_keys.setGeometry(
            QtCore.QRect(176, 270, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.connector_space_bar_keys.sizePolicy().hasHeightForWidth())
        self.connector_space_bar_keys.setSizePolicy(sizePolicy)
        self.connector_space_bar_keys.setStyleSheet("font-size: 10pt;")
        self.connector_space_bar_keys.setMaxLength(30)
        self.connector_space_bar_keys.setObjectName("connector_space_bar_keys")
        self.connector_none_keys = QtWidgets.QLineEdit(self.centralwidget)
        self.connector_none_keys.setGeometry(QtCore.QRect(334, 270, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.connector_none_keys.sizePolicy().hasHeightForWidth())
        self.connector_none_keys.setSizePolicy(sizePolicy)
        self.connector_none_keys.setStyleSheet("font-size: 10pt;")
        self.connector_none_keys.setMaxLength(30)
        self.connector_none_keys.setObjectName("connector_none_keys")
        self.label_connector_none = QtWidgets.QLabel(self.centralwidget)
        self.label_connector_none.setGeometry(QtCore.QRect(340, 240, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_connector_none.sizePolicy().hasHeightForWidth())
        self.label_connector_none.setSizePolicy(sizePolicy)
        self.label_connector_none.setBaseSize(QtCore.QSize(0, 0))
        self.label_connector_none.setStyleSheet("font-size: 12pt;")
        self.label_connector_none.setScaledContents(False)
        self.label_connector_none.setObjectName("label_connector_none")
        self.groupConnect = QtWidgets.QGroupBox(self.centralwidget)
        self.groupConnect.setGeometry(QtCore.QRect(10, 10, 481, 71))
        self.groupConnect.setTitle("")
        self.groupConnect.setObjectName("groupConnect")
        self.label_client_name_for_share = QtWidgets.QLabel(self.centralwidget)
        self.label_client_name_for_share.setGeometry(
            QtCore.QRect(181, 90, 141, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_client_name_for_share.sizePolicy().hasHeightForWidth())
        self.label_client_name_for_share.setSizePolicy(sizePolicy)
        self.label_client_name_for_share.setBaseSize(QtCore.QSize(0, 0))
        self.label_client_name_for_share.setStyleSheet("font-size: 12pt;")
        self.label_client_name_for_share.setScaledContents(False)
        self.label_client_name_for_share.setObjectName(
            "label_client_name_for_share")
        self.client_name_for_share = QtWidgets.QLineEdit(self.centralwidget)
        self.client_name_for_share.setGeometry(QtCore.QRect(175, 120, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.client_name_for_share.sizePolicy().hasHeightForWidth())
        self.client_name_for_share.setSizePolicy(sizePolicy)
        self.client_name_for_share.setStyleSheet("font-size: 10pt;")
        self.client_name_for_share.setText("")
        self.client_name_for_share.setMaxLength(30)
        self.client_name_for_share.setClearButtonEnabled(False)
        self.client_name_for_share.setObjectName("client_name_for_share")
        self.groupClients = QtWidgets.QGroupBox(self.centralwidget)
        self.groupClients.setGeometry(QtCore.QRect(10, 90, 481, 71))
        self.groupClients.setTitle("")
        self.groupClients.setObjectName("groupClients")
        self.groupHotkeys = QtWidgets.QGroupBox(self.centralwidget)
        self.groupHotkeys.setGeometry(QtCore.QRect(10, 170, 481, 141))
        self.groupHotkeys.setTitle("")
        self.groupHotkeys.setObjectName("groupHotkeys")
        self.groupClients.raise_()
        self.groupHotkeys.raise_()
        self.groupConnect.raise_()
        self.ip.raise_()
        self.port.raise_()
        self.label_ip.raise_()
        self.button_apply.raise_()
        self.label_port.raise_()
        self.copy_join_keys.raise_()
        self.label_copy_join_keys.raise_()
        self.copy_share_keys.raise_()
        self.label_copy_share_keys.raise_()
        self.label_error.raise_()
        self.client_name.raise_()
        self.label_client_name.raise_()
        self.label_client_name_for_sync.raise_()
        self.client_name_for_sync.raise_()
        self.connector_enter_keys.raise_()
        self.label_connector_enter_keys.raise_()
        self.label_connector_space_bar_keys.raise_()
        self.connector_space_bar_keys.raise_()
        self.connector_none_keys.raise_()
        self.label_connector_none.raise_()
        self.label_client_name_for_share.raise_()
        self.client_name_for_share.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Share Сlipboard"))
        self.ip.setPlaceholderText(_translate("MainWindow", " 127.0.0.1 *"))
        self.port.setPlaceholderText(_translate("MainWindow", " 7000 *"))
        self.label_ip.setText(_translate(
            "MainWindow", "<html><head/><body><p>Адрес сервера</p></body></html>"))
        self.button_apply.setText(_translate("MainWindow", "Применить"))
        self.button_apply.setShortcut(_translate("MainWindow", "1"))
        self.label_port.setText(_translate(
            "MainWindow", "<html><head/><body><p>Порт</p></body></html>"))
        self.copy_join_keys.setPlaceholderText(
            _translate("MainWindow", " <ctrl>+<shift>+c"))
        self.label_copy_join_keys.setText(_translate(
            "MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Копирование +</span></p></body></html>"))
        self.copy_share_keys.setPlaceholderText(
            _translate("MainWindow", " <ctrl>+<alt>+p"))
        self.label_copy_share_keys.setText(_translate(
            "MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Поделиться</span></p></body></html>"))
        self.label_error.setText(
            _translate("MainWindow", "<html><head/><body><p/></body></html>"))
        self.client_name.setPlaceholderText(
            _translate("MainWindow", " Ваше имя *"))
        self.label_client_name.setText(_translate(
            "MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Имя</span></p></body></html>"))
        self.label_client_name_for_sync.setText(_translate(
            "MainWindow", "<html><head/><body><p>Синхронизация</p></body></html>"))
        self.client_name_for_sync.setPlaceholderText(
            _translate("MainWindow", "Имя клиента, ..."))
        self.connector_enter_keys.setPlaceholderText(
            _translate("MainWindow", " <ctrl>+1"))
        self.label_connector_enter_keys.setText(_translate(
            "MainWindow", "<html><head/><body><p>Новая строка</p></body></html>"))
        self.label_connector_space_bar_keys.setText(_translate(
            "MainWindow", "<html><head/><body><p>Пробел</p></body></html>"))
        self.connector_space_bar_keys.setPlaceholderText(
            _translate("MainWindow", " <ctrl>+2"))
        self.connector_none_keys.setPlaceholderText(
            _translate("MainWindow", " <ctrl>+3"))
        self.label_connector_none.setText(_translate(
            "MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Слитно</span></p></body></html>"))
        self.label_client_name_for_share.setText(_translate(
            "MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Делиться c:</span></p></body></html>"))
        self.client_name_for_share.setPlaceholderText(
            _translate("MainWindow", "Имя клиента, ..."))


# f55a44 red
# 499c54 green
# 287bde blue
# cbcdc1 wite
# ffc66d yellow


class LogWindow(QtWidgets.QTextEdit):
    newMessage = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1300, 800)
        self.setReadOnly(True)
        self.newMessage.connect(self.log)
        self.message = None

    @QtCore.pyqtSlot(str, int)
    def log(self, message, level):
        color = '#cbcdc1'
        if level == logging.DEBUG:
            color = '#ffc66d'  # yellow
        if level == logging.INFO:
            self.setStyleSheet('color: #499c54;')  # green
            color = '#499c54'  # green
        if level == logging.WARNING:
            self.setStyleSheet('color: #287bde;')  # blue
            color = '#287bde'  # blue
        if level == logging.ERROR:
            self.setStyleSheet('color: #f55a44;')  # red
            color = '#f55a44'  # red
        # ------------------------------------------------------------ #
        self.setStyleSheet('background-color: #2b2b2b;')
        self.message = f"<span style='color:{color}'>'{message}'</span>"
        # ------------------------------------------------------------ #
        self.message = self.message.replace(
            "{", "</span><span style='color: #9D57AE'>{"
        )
        # ------------------------------------------------------------ #
        self.append(self.message)
        # скролл вниз ------------ #
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def closeEvent(self, event):
        """ Перехват события закрытия окна """
        event.ignore()
        self.hide()


class ShowUiMainWindow(QtWidgets.QMainWindow):
    tray_icon = None

    def __init__(self,
                 callback_settings_update,
                 callback_apply_received_data
                 ):
        super(ShowUiMainWindow, self).__init__()
        assert callable(callback_settings_update)
        assert callable(callback_apply_received_data)
        self.callback_settings_update = callback_settings_update
        self.callback_apply_received_data = callback_apply_received_data
        # ----------------------------------------------------------------------
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        # ----------------------------------------------------------------------
        self.log_window = LogWindow()
        # ----------------------------------------------------------------------
        ''' Кнопка "Применить" '''
        self.ui.button_apply.clicked.connect(self.apply_parameters)
        # ----------------------------------------------------------------------
        ''' Сворачивание в трей '''
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QStyle.SP_ComputerIcon))
        # self.tray_icon.setIcon(QIcon('icon.ico'))

        apply_data_action = QAction("Принять данные", self)
        show_action = QAction("Показать", self)
        log_action = QAction("Показать лог", self)
        hide_action = QAction("Свернуть в трей", self)
        quit_action = QAction("Закрыть", self)
        #
        apply_data_action.triggered.connect(
            lambda: self.callback_apply_received_data())
        show_action.triggered.connect(self.show)
        log_action.triggered.connect(lambda: self.log_window.show())
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        #
        tray_menu = QMenu()
        tray_menu.addAction(apply_data_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(log_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        #
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        # ----------------------------------------------------------------------
        self.old_settings = None
        # ----------------------------------------------------------------------

    def on_tray_icon_activated(self, reason):
        """ Показать окно двойным кликом по иконке в трее """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
        #

    def closeEvent(self, event):
        """ Перехват события закрытия окна """
        event.ignore()
        self.hide()

    # def changeEvent(self, event):
    #     """ Перехват события сворачивания окна """
    #     if self.isMinimized():
    #         self.hide() # отправить в трей
    #         self.tray_icon.showMessage(
    #             "Уведомление",
    #             "Приложение свернулось в трей",
    #             QSystemTrayIcon.Information,
    #             1000
    #         )

    # --------------------------------------------------------------------------

    def window_placement(self):
        """ Место размещения окна на экране """
        frame_gm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos())
        center_point = QtWidgets.QApplication.desktop().screenGeometry(
            screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    # --------------------------------------------------------------------------

    @staticmethod
    def _list_to_string(value):
        return ', '.join(value)

    def _set_settings(self, settings: app_settings.AppSettings, update=True):
        """ Вывод имеющихся параметров в поля ввода если они есть """
        self.old_settings = settings
        #
        self.ui.ip.setText(settings.ip)
        self.ui.port.setText(settings.port)
        self.ui.client_name.setText(settings.client_name)
        self.ui.client_name_for_sync.setText(
            self._list_to_string(settings.client_name_for_sync)
        )
        self.ui.client_name_for_share.setText(
            self._list_to_string(settings.client_name_for_share)
        )
        self.ui.copy_join_keys.setText(settings.copy_join_keys)
        self.ui.copy_share_keys.setText(settings.share_keys)
        self.ui.connector_space_bar_keys.setText(
            settings.connector_space_bar_keys)
        self.ui.connector_enter_keys.setText(settings.connector_new_line_keys)
        self.ui.connector_none_keys.setText(settings.connector_none_keys)
        #
        if update:
            self.update()
        #

    # --------------------------------------------------------------------------

    def show_gui(self, settings) -> None:
        self._set_settings(settings, update=False)
        self.window_placement()
        return super(ShowUiMainWindow, self).hide()

    # --------------------------------------------------------------------------

    def show_msg(self, msg, success=False, popup=False):
        if popup:
            self.tray_icon.showMessage(
                "Share Clipboard",
                msg,
                QSystemTrayIcon.Information,
                1000,
            )
        if success:
            self.ui.label_error.setStyleSheet('color: #00CC00')  # Green
            self.ui.label_error.setText(msg)
            self.ui.label_error.update()
            return
        self.ui.label_error.setStyleSheet('color: #FF0000')  # Red
        self.ui.label_error.setText(msg)
        self.ui.label_error.update()

    # --------------------------------------------------------------------------

    def apply_parameters(self) -> None:
        """ Применение параметров """
        client_name_for_sync = self.ui.client_name_for_sync.text()
        if not client_name_for_sync:
            client_name_for_sync = []
        client_name_for_share = self.ui.client_name_for_share.text()
        if not client_name_for_share:
            client_name_for_share = []

        new_settings = app_settings.AppSettings(
            client_id=self.old_settings.client_id,
            ip=self.ui.ip.text(),
            port=self.ui.port.text(),
            client_name=self.ui.client_name.text(),
            client_name_for_sync=client_name_for_sync,
            client_name_for_share=client_name_for_share,
            copy_join_keys=self.ui.copy_join_keys.text(),
            share_keys=self.ui.copy_share_keys.text(),
            connector_space_bar_keys=self.ui.connector_space_bar_keys.text(),
            connector_new_line_keys=self.ui.connector_enter_keys.text(),
            connector_none_keys=self.ui.connector_none_keys.text(),
        )
        self.callback_settings_update(
            new_settings,
        )
        # ----------------------------------------------------------------------
