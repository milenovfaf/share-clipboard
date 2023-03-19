import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp, \
    QFileDialog
from PyQt5.QtCore import Qt

import app_settings
import gui_qtdesigner
import service

import logging
log = logging.getLogger(__name__)


def _window_placement(window):
    """ Место размещения окна на экране """
    frame_gm = window.frameGeometry()
    screen = QtWidgets.QApplication.desktop().screenNumber(
        QtWidgets.QApplication.desktop().cursor().pos())
    center_point = QtWidgets.QApplication.desktop().screenGeometry(
        screen).center()
    frame_gm.moveCenter(center_point)
    window.move(frame_gm.topLeft())


# class DialogWindow(QtWidgets.QWidget):
#     def __init__(self, callback_create_image_file):
#         super().__init__()
#         self.callback_create_image_file = callback_create_image_file
#
#     def directory_selection(self):
#         default_path = service.get_desktop_path()
#         dialog = QFileDialog()
#         dialog.setWindowTitle('Выберите директорию')
#         dialog.setAcceptMode(QFileDialog.AcceptSave)
#         dialog.setDefaultSuffix('png')
#         # default_filename = 'Новый_файл.png'
#         # file_dialog.selectFile(default_filename)
#         file_path, _ = dialog.getSaveFileName(
#             directory=default_path,
#             filter='Image Files (*.png *.jpg *.bmp)',
#             options=QFileDialog.DontUseNativeDialog,
#         )
#         directory = os.path.dirname(file_path)
#         filename = os.path.basename(file_path)
#         #
#         self.callback_create_image_file(directory, filename)
#
#     def closeEvent(self, event):
#         """ Перехват события закрытия окна """
#         # event.accept()
#         # QtWidgets.QApplication.quit()
#         event.ignore()
#         self.hide()


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
        # f55a44 red
        # 499c54 green
        # 287bde blue
        # cbcdc1 white
        # ffc66d yellow
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
                 callback_apply_received_share_data,
                 callback_create_image_file,
                 callback_show_image,
                 callback_is_need_reconnect,
                 ):
        super(ShowUiMainWindow, self).__init__()
        assert callable(callback_settings_update)
        assert callable(callback_apply_received_share_data)
        assert callable(callback_is_need_reconnect)
        self.callback_settings_update = callback_settings_update
        self.callback_apply_received_share_data = callback_apply_received_share_data
        self.callback_create_image_file = callback_create_image_file
        self.callback_show_image = callback_show_image
        self.callback_is_need_reconnect = callback_is_need_reconnect
        # ----------------------------------------------------------------------
        self.ui = gui_qtdesigner.UiMainWindow()
        self.ui.setupUi(self)
        # ----------------------------------------------------------------------
        self.dialog_window = DialogWindow(self.callback_create_image_file)
        # ----------------------------------------------------------------------
        # self.image_window = ImageWindow(self.callback_create_image_file)
        # ----------------------------------------------------------------------
        self.log_window = LogWindow()
        # ----------------------------------------------------------------------
        ''' Кнопка "Применить" '''
        self.ui.button_apply.clicked.connect(self.apply_parameters)
        # ----------------------------------------------------------------------
        ''' Трей '''
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(
        #     self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.show_icon()
        self.tray_icon.setContextMenu(self.show_context_menu())
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        # ----------------------------------------------------------------------
        self.old_settings = None
        # ----------------------------------------------------------------------

    def show_context_menu(self):
        apply_data_action = QAction('Принять данные', self)
        save_on_desktop_action = QAction('Сохранить на рабочий стол', self)
        # save_action = QAction('Сохранить как', self)
        is_need_reconnect_action = QAction("Переподключить", self)
        show_image_action = QAction('Показать изображение', self)
        log_action = QAction('Показать лог', self)
        hide_action = QAction('Свернуть в трей', self)
        quit_action = QAction('Закрыть', self)
        #
        apply_data_action.triggered.connect(
            lambda: self.callback_apply_received_share_data()
        )
        save_on_desktop_action.triggered.connect(
            lambda: self.callback_create_image_file(
                directory=service.get_desktop_path()
            ))
        # save_action.triggered.connect(
        #     lambda: self.dialog_window.directory_selection()
        # )
        is_need_reconnect_action.triggered.connect(
            lambda: self.callback_is_need_reconnect()
        )
        show_image_action.triggered.connect(
            lambda: self.callback_show_image()
        )
        log_action.triggered.connect(
            lambda: self.log_window.show()
        )
        hide_action.triggered.connect(
            self.hide
        )
        quit_action.triggered.connect(
            qApp.quit
        )
        #
        tray_menu = QMenu()
        tray_menu.addAction(apply_data_action)
        tray_menu.addSeparator()
        tray_menu.addAction(show_image_action)
        tray_menu.addAction(save_on_desktop_action)
        # tray_menu.addAction(save_action)
        tray_menu.addSeparator()
        tray_menu.addAction(log_action)
        tray_menu.addSeparator()
        tray_menu.addAction(is_need_reconnect_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        return tray_menu

    def on_tray_icon_activated(self, reason):
        """ Показать или скрыть окно одинарным кликом по иконке в трее """
        # if reason == QSystemTrayIcon.DoubleClick:
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
        #

    def show_icon(self, color='blue'):
        """ Отображение иконки в трее """
        icon = os.path.join(service.get_base_path(), "icons", "icon_blue.ico")
        if color is 'red':
            icon = os.path.join(service.get_base_path(), 'icons', 'icon_red.ico')
        if color is 'green':
            icon = os.path.join(service.get_base_path(), 'icons', 'icon_green.ico')
        #
        self.tray_icon.setIcon(QIcon(icon))
        #

    def closeEvent(self, event):
        """ Перехват события закрытия окна """
        event.ignore()
        self.hide()

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
        _window_placement(self)
        return super(ShowUiMainWindow, self).hide()

    # --------------------------------------------------------------------------

    def show_msg(self, msg, success=False, popup=False):
        """ Вывод сообщений """
        if popup:
            self.tray_icon.showMessage(
                "Share Clipboard",
                msg,
                QSystemTrayIcon.Information,
                2000,
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
        """ Применение новых параметров """
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
