# -*- coding: utf-8 -*-
import sys
import serial
import datetime
import base64
import os
# import shutil
# import win32api
# import win32con
import ctypes
import configparser

from serial.tools.list_ports import comports
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer, QPoint
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QDesktopWidget

# base64
from ImgBase64 import close_first as close_first
from ImgBase64 import close_latter as close_latter
from ImgBase64 import maximize_first as maximize_first
from ImgBase64 import maximize_latter as maximize_latter
from ImgBase64 import normal_first as normal_first
from ImgBase64 import normal_latter as normal_latter
from ImgBase64 import minimize_first as minimize_first
from ImgBase64 import minimize_latter as minimize_latter
from ImgBase64 import title_icon as title_icon
from ImgBase64 import icon as icon

from CommAssistant_UI import Ui_Form


# 创建文件夹
def CreateDocument(docPack):

    isExist = os.path.exists(docPack)

    if not isExist:     # 不存在该文件夹
        os.mkdir(docPack)       # 创建文件夹

        # win32api.SetFileAttributes(docPack, win32con.FILE_ATTRIBUTE_HIDDEN)  # 隐藏文件夹

        # 从指定目录下加载图片
        LoadImg('C:/images/close_first.png', close_first)
        LoadImg('C:/images/close_latter.png', close_latter)
        LoadImg('C:/images/maximize_first.png', maximize_first)
        LoadImg('C:/images/maximize_latter.png', maximize_latter)
        LoadImg('C:/images/normal_first.png', normal_first)
        LoadImg('C:/images/normal_latter.png', normal_latter)
        LoadImg('C:/images/minimize_first.png', minimize_first)
        LoadImg('C:/images/minimize_latter.png', minimize_latter)
        LoadImg('C:/images/title_icon.png', title_icon)
        LoadImg('C:/images/icon.ico', icon)     # 这个图片格式必须为.ico格式，否则无法显示
        print('文件夹创建成功')
    else:       # 如果已经存在文件夹，只需在该文件夹下加载必要的图片
        # 以下操作主要防止用户不小心删除相关文件
        if not os.path.exists('C:/images/close_first.png'):
            LoadImg('C:/images/close_first.png', close_first)

        if not os.path.exists('C:/images/close_latter.png'):
            LoadImg('C:/images/close_latter.png', close_latter)

        if not os.path.exists('C:/images/maximize_first.png'):
            LoadImg('C:/images/maximize_first.png', maximize_first)

        if not os.path.exists('C:/images/maximize_latter.png'):
            LoadImg('C:/images/maximize_latter.png', maximize_latter)

        if not os.path.exists('C:/images/normal_first.png'):
            LoadImg('C:/images/normal_first.png', normal_first)

        if not os.path.exists('C:/images/normal_latter.png'):
            LoadImg('C:/images/normal_latter.png', normal_latter)

        if not os.path.exists('C:/images/minimize_first.png'):
            LoadImg('C:/images/minimize_first.png', minimize_first)

        if not os.path.exists('C:/images/minimize_latter.png'):
            LoadImg('C:/images/minimize_latter.png', minimize_latter)

        if not os.path.exists('C:/images/title_icon.png'):
            LoadImg('C:/images/title_icon.png', title_icon)

        if not os.path.exists('C:/images/icon.ico'):
            LoadImg('C:/images/icon.ico', icon)
        print('文件创建成功')
        return None


# 加载图片资源
def LoadImg(picPath, name):

    tmp = open(picPath, 'wb+')  # 在指定目录下创建文件
    tmp.write(base64.b64decode(name))  # 解码图片
    tmp.close()  # 关闭写


class CommAssistant(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(CommAssistant, self).__init__(parent)

        CreateDocument('C:/images')        # 在C盘目录下创建images文件夹，若已存在相关文件则无须再次加载

        self.setupUi(self)      # 初始化界面
        self.InitSetting()      # 初始化配置/加载上一次使用的数据
        # self.MoveCenter()       # 将窗口移到屏幕中间

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myappid')        # 主要是解决Windows任务栏下无法显示图标的问题
        self.setWindowIcon(QIcon('C:\images\icon.ico'))     # 设置标题栏、任务栏等的图标

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint)     # 隐藏标题栏，支持右键菜单，允许最小化还原

        self.ser = None

        self.padding = 4        # 设置边界宽度为5，用于边缘拉伸

        # 窗口移动及拉伸的状态位
        self.move_drag = False      # 移动状态
        self.move_drag_position = 0     # 移动距离变量
        self.corner_drag = False        # 右下角拉伸状态
        self.corner_rect = 0        # 右下角拉伸位置变量
        self.right_drag = False     # 右侧拉伸状态
        self.right_rect = 0     # 右侧拉伸位置变量
        self.bottom_drag = False        # 下方拉伸状态
        self.bottom_rect = 0        # 下方拉伸位置变量

        # 初始化接收发送数量
        self.receive_num = 0
        self.ReceiveNumlabel.setText('Receive: ' + '{:d}'.format(self.receive_num))
        self.send_num = 0
        self.SendNumlabel.setText('Send: ' + '{:d}'.format(self.send_num))

        self.RefreshCOM()        # 刷新串口列表

        self.ser = serial.Serial()              # 实例化串口
        self.timer_date = QTimer(self)          # 实例化时间定时器
        self.timer_receive = QTimer(self)       # 实例化接收定时器
        self.timer_send = QTimer(self)          # 实例化发送定时器，暂时没有用到定时发送
        self.timer_refresh = QTimer(self)       # 实例化刷新串口定时器

        self.timer_refresh.setInterval(100)     # 设置定时器时间为100ms
        self.timer_refresh.start()              # 开启串口刷新定时器
        self.timer_refresh.timeout.connect(self.RefreshCOM)     # 定时刷新串口列表

        self.timer_date.setInterval(500)        # 设置定时器时间为500ms
        self.timer_date.start()                 # 开启时间定时器
        self.timer_date.timeout.connect(self.RefreshTime)            # 定时刷新当前时间

        self.timer_receive.timeout.connect(self.ReceiveData)        # 定时接收
        self.timer_send.timeout.connect(self.SendData)              # 定时发送

        self.OpenButton.clicked.connect(self.OpenOrCloseSerial)     # 打开/关闭串口
        self.RefreshComButton.clicked.connect(self.RefreshCOM)      # 刷新串口
        self.SendButton.clicked.connect(self.SendData)              # 发送按钮

    def InitSetting(self):
        global config
        if not os.path.exists('setting.ini'):       # 检测是否存在配置文件
            open('setting.ini', 'w')        # 创建配置文件

        config = configparser.ConfigParser()    # 加载现有配置文件
        config.read('setting.ini')      # 读取ini文件

        if not config.has_section('globals'):       # 如果为空
            config['globals'] = {'baudrate': '115200', 'stop': '1', 'data': '8', 'parity': '无校验', 'string': 'Hello'}        # 向配置文件写入数据
            with open('setting.ini', 'w') as configfile:        # with用法，先打开数据再写
                config.write(configfile)
        # 把配置文件的数据加载到窗口
        self.SerialBaudRateComboBox.setCurrentText(config.get('globals', 'baudrate'))
        self.SerialStopBitsComboBox.setCurrentText(config.get('globals', 'stop'))
        self.SerialDataBitsComboBox.setCurrentText(config.get('globals', 'data'))
        self.SerialParityComboBox.setCurrentText(config.get('globals', 'parity'))
        self.SendEdit.insertPlainText(config.get('globals', 'string'))

    def MoveCenter(self):       # 将窗口移动到中间，备用
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def RefreshTime(self):       # 刷新界面右下角的时间显示，并显示
        current = datetime.datetime.now()
        self.Timelabel.setText('当前时间 ' + '{:02d}'.format(current.hour) +
                               ':{:02d}'.format(current.minute) + ':{:02d}'.format(current.second))

    def ReceiveData(self):      # 接收数据
        global receive_bytes_num
        if self.ser.is_open:        # 是否打开串口
            # noinspection PyBroadException
            # 这里主要是处理自定义波特率时非法输入设置的
            try:
                self.ser.baudrate = int(self.SerialBaudRateComboBox.currentText())
            except Exception:
                QMessageBox.critical(self, 'Message', '请先关闭串口')
                self.timer_receive.stop()
                self.ser.close()
                self.OpenButton.setText(u'打开串口')
                return None
            self.ser.baudrate = int(self.SerialBaudRateComboBox.currentText())      # 读取用户选择的波特率
            self.ser.stopbits = int(self.SerialStopBitsComboBox.currentText())      # 读取用户选择的停止位
            self.ser.bytesize = int(self.SerialDataBitsComboBox.currentText())      # 读取用户选择的数据位

            serial_parity = self.SerialParityComboBox.currentText()     # 获取当前设置值
            if serial_parity == '无校验':
                self.ser.parity = serial.PARITY_NONE            # 设置当前的文本为校验方式
            elif serial_parity == '奇校验':
                self.ser.parity = serial.PARITY_ODD             # 设置当前的文本为校验方式
            elif serial_parity == '偶校验':
                self.ser.parity = serial.PARITY_EVEN            # 设置当前的文本为校验方式
            else:
                return None

            # noinspection PyBroadException
            try:
                receive_bytes_num = self.ser.inWaiting()       # 获取Output buffer中的字节数
            except Exception:     # 串口拔出错误
                self.timer_receive.stop()       # 关闭接收定时器
                self.timer_send.stop()          # 关闭发送定时器
                self.ser.close()                # 关闭串口
                self.ser = None                 # 串口无效

            if receive_bytes_num > 0:       # 接收数据非空
                data = self.ser.read(receive_bytes_num)       # 读取串口数据
                print(data)        # 测试：打印串口数据
                if self.HexDisplayCheckBox.checkState():        # 十六进制显示
                    out_string = ''     # 接收数据buffer，存放16进制数
                    for i in range(0, len(data)):
                        out_string = out_string + '{:02X}'.format(data[i]) + ' '        # 转换为十六进制
                    textCursor = self.ReceiveEdit.textCursor()          # 获取到ReceiveEdit的光标
                    self.ReceiveEdit.moveCursor(textCursor.End)         # 滚动到底部
                    self.ReceiveEdit.insertPlainText(out_string)        # 将数据输出到界面
                else:
                    try:
                        print(data)
                        data = data.decode('gbk', 'ignore')     # 转化成gbk字符输出到串口,ignore主要处理某些数据无法用gbk解释
                    except Exception as e:      # try except语法可以做调试用
                        print(e)
                    if self.TimeShowCheckBox.checkState():      # 打开时间戳
                        data = data.strip('\r\n')       # 去掉换行符
                        current = datetime.datetime.now()       # 获取时间
                        textCursor = self.ReceiveEdit.textCursor()  # 获取到ReceiveEdit的光标
                        self.ReceiveEdit.moveCursor(textCursor.End)  # 滚动到底部
                        # 插入时间
                        self.ReceiveEdit.insertPlainText(data + ' 【{0:02d}:{1:02d}:{2:02d}:{3:03d}】\n'.format(current.hour, current.minute,
                                                                                                              current.second,
                                                                                                              int(current.microsecond*1e-3)))
                    else:
                        textCursor = self.ReceiveEdit.textCursor()      # 获取到ReceiveEdit的光标
                        self.ReceiveEdit.moveCursor(textCursor.End)     # 滚动到底部
                        self.ReceiveEdit.insertPlainText(data)          # 插入数据

                self.receive_num = self.receive_num + receive_bytes_num       # 统计接收字符的数量
                self.ReceiveNumlabel.setText('Receive: ' + '{:d}'.format(self.receive_num))     # 显示接收数据字节数
            else:
                return None

    def SendData(self):
        if self.ser.is_open:        # 如果串口已经打开
            input_string = self.SendEdit.toPlainText()      # 获取textedit文本内容
            if input_string != '':
                if self.HexSendCheckBox.checkState():       # 十六进制发送
                    input_string = input_string.strip()     # 删除前后的空格
                    send_list = []      # 发送列表
                    while input_string != '':       # 循环，知道input_string中的数据全部放到send_list
                        try:
                            num_of_bytes = int(input_string[0:2], 16)       # 将其中输入的Hex转换成int型
                        except ValueError:      # 输入的值如果无法转换成整形，即输入错误
                            QMessageBox.critical(self, 'Message', '请输入十六进制数据，以空格分开!')
                            return None

                        input_string = input_string[2:]     # 去除排在前面的字节
                        input_string = input_string.strip()     # 去除空格

                        send_list.append(num_of_bytes)      # 添加到发送列表
                    input_string = bytes(send_list)     # 转换成字节，存回输入缓冲区中

                else:       # 文本发送
                    if self.SendBlankCheckBox.checkState():  # 发送新行,即插入\r\n
                        input_string = input_string + '\r\n'

                    input_string = input_string.encode('gbk')       # 输出的数据为gbk码

                # noinspection PyBroadException
                try:
                    send_bytes_num = self.ser.write(input_string)       # 发送数据,并返回发送字节数
                except Exception:       # 发送失败
                    self.timer_send.stop()      # 停止发送Timer，暂时没有用到定时发送，有无也可
                    self.ser.close()        # 关闭串口

                    self.OpenButton.setChecked(False)
                    self.OpenButton.setText(u'打开串口')
                    return None

                self.send_num = self.send_num + send_bytes_num      # 统计发送字节数
                self.SendNumlabel.setText('Send: ' + '{:d}'.format(self.send_num))

        else:
            self.timer_send.stop()      # 停止发送Timer，暂时没有用到定时发送，有无也可
            QMessageBox.critical(self, 'Message', '请打开串口')

    def RefreshCOM(self):
        port_list = serial.tools.list_ports.comports()      # 获取所有串口的端口号

        if len(port_list) == 0:     # 如果串口列表为0，即没有端口
            self.SerialCOMComboBox.clear()
            # QMessageBox.critical(self, 'Message', '没有可用的串口或当前串口被占用')
            # self.move(10)
        else:
            for port, desc, hwid in comports():     # 识别串口
                if self.SerialCOMComboBox.findText(port) != -1:     # 如果combox中已经有该串口，则不需再次添加
                    pass
                else:
                    self.SerialCOMComboBox.addItem(port)        # 把串口号添加到Box

    def OpenOrCloseSerial(self):        # 打开/关闭串口操作
        if not self.ser.is_open:        # 如果串口没有打开
            # noinspection PyBroadException
            try:
                self.ser.timeout = 1        # 读超时设置
                self.ser.xonxoff = 0        # 软件流控
                self.ser.port = self.SerialCOMComboBox.currentText()        # 端口
                # noinspection PyBroadException
                # 这里也是处理自定义波特率时非法输入设置的
                try:
                    self.ser.baudrate = int(self.SerialBaudRateComboBox.currentText())
                except Exception:
                    QMessageBox.critical(self, 'Message', '请输入正确的波特率')
                    return None
                self.ser.stopbits = int(self.SerialStopBitsComboBox.currentText())
                self.ser.bytesize = int(self.SerialDataBitsComboBox.currentText())

                serial_parity = self.SerialParityComboBox.currentText()     # 获取当前设置值
                if serial_parity == '无校验':
                    self.ser.parity = serial.PARITY_NONE            # 设置当前的文本为校验方式
                elif serial_parity == '奇校验':
                    self.ser.parity = serial.PARITY_ODD             # 设置当前的文本为校验方式
                elif serial_parity == '偶校验':
                    self.ser.parity = serial.PARITY_EVEN            # 设置当前的文本为校验方式
                else:
                    return None
                self.timer_receive.setInterval(20)      # 设置定时器时间为20ms
                self.timer_receive.start()      # 开启定时器
                self.ser.open()     # 开启端口
            except Exception:
                QMessageBox.critical(self, 'Message', '没有可用的串口或当前串口被占用')
            else:
                self.SerialCOMComboBox.setEnabled(False)        # 关闭串口选择功能
                self.OpenButton.setText(u'关闭串口')            # ‘打开串口’改为‘关闭串口’
        else:       # 如果串口已经打开,再次点击
            self.ser.close()        # 关闭串口
            self.timer_receive.stop()       # 关闭定时器
            self.SerialCOMComboBox.setEnabled(True)     # 打开串口按钮使能
            self.OpenButton.setText(u'打开串口')

    def on_SerialBaudRateComboBox_activated(self):
        if self.SerialBaudRateComboBox.currentText() == '自定义':
            self.SerialBaudRateComboBox.setEditable(True)       # 打开可编辑功能
        else:
            self.SerialBaudRateComboBox.setEditable(False)      # 关闭可编辑功能

    def on_HexDisplayCheckBox_stateChanged(self):       # 16进制显示复选框状态发生变化
        temp_string = self.ReceiveEdit.toPlainText()        # 读取输出框的数据
        if temp_string != '':       # 数据非空
            if self.HexDisplayCheckBox.checkState():        # 如果选择十六进制显示
                temp_hex = temp_string.encode('gbk')        # 解码
                display_hex = ''
                for i in range(0, len(temp_hex)):
                    display_hex = display_hex + '{:02X}'.format(temp_hex[i]) + ' '  # 转换为十六进制
                self.ReceiveEdit.clear()        # 清空输入框
                self.ReceiveEdit.insertPlainText(display_hex)       # 输出十六进制数据
            if not self.HexDisplayCheckBox.checkState():        # 没有选择十六进制显示
                temp_hex = self.SendEdit.toPlainText()  # 获取textedit文本内容
                temp_hex = temp_hex.strip()     # 清除前后的空格
                display_string = bytes.fromhex(temp_hex).decode('gbk')  # 转换成字符串
                self.ReceiveEdit.clear()        # 清除输出框
                self.ReceiveEdit.insertPlainText(display_string)        # 插入数据
        else:
            return None

    def on_HexSendCheckBox_stateChanged(self):      # 发送栏的16进制复选框状态发生变化，这个跟显示框的差不多
        input_data = self.SendEdit.toPlainText()        # 获取textedit文本内容
        if input_data != '':        # 输入非空
            if self.HexSendCheckBox.checkState():       # 16进制发送选中
                input_string = input_data.encode("gbk")     # 解码
                print(input_string)
                string_to_hex = ''      # 解码出来的数据需要重新整理格式
                for i in range(0, len(input_string)):
                    string_to_hex = string_to_hex + '{:02X}'.format(input_string[i]) + ' '  # 转换为十六进制
                print(string_to_hex)
                self.SendEdit.clear()
                self.SendEdit.insertPlainText(string_to_hex)
            if not self.HexSendCheckBox.checkState():
                input_data = self.SendEdit.toPlainText()        # 获取textedit文本内容
                input_data = input_data.strip()     # 清楚前后空格
                # 限制用户输入非法的十六进制
                try:
                    int(input_data[0:2], 16)
                except ValueError:
                    QMessageBox.critical(self, 'Message', '请输入十六进制数据，以空格分开!')
                    return None

                print(input_data)
                hex_to_string = bytes.fromhex(input_data).decode('gbk')       # 转换成字符串
                print(hex_to_string)
                self.SendEdit.clear()
                self.SendEdit.insertPlainText(hex_to_string)
        else:
            pass

    def resizeEvent(self, QResizeEvent):        # 当窗口大小发生变化时，边框的位置需要重新计算，为边缘拉伸做准备
        try:
            self.corner_rect = [QPoint(x, y) for x in range(self.width() - self.padding, self.width() + 1)
                                for y in range(self.height() - self.padding, self.height() + 1)]

            self.right_rect = [QPoint(x, y) for x in range(self.width() - self.padding, self.width() + 1)
                               for y in range(1, self.height() - self.padding)]

            self.bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self.padding)
                                for y in range(self.height() - self.padding, self.height() + 1)]
        except Exception as e:
            print(e)

    def mouseDoubleClickEvent(self, QMouseEvent):       # 双击事件
        if (QMouseEvent.button() == Qt.LeftButton) and (QMouseEvent.y() < self.TitleBar.height()):      # 鼠标双击在标题栏位置
            if self.isMaximized():      # 如果窗口已经最大化
                self.showNormal()       # 变为初始时大小
            else:
                self.showMaximized()        # 实现窗口最大化

    def mousePressEvent(self, event):       # 鼠标点击事件
            if (event.button() == Qt.LeftButton) and (event.pos() in self.corner_rect):     # 鼠标点击了右下角
                self.corner_drag = True
                event.accept()

            elif (event.button() == Qt.LeftButton) and (event.pos() in self.right_rect):        # 鼠标点击了右边缘
                self.right_drag = True
                event.accept()

            elif (event.button() == Qt.LeftButton) and (event.pos() in self.bottom_rect):       # 鼠标点击了下边缘
                self.bottom_drag = True
                event.accept()

            elif (event.button() == Qt.LeftButton) and (event.y() < self.TitleBar.height()):      # 鼠标点击在标题栏位置
                self.move_drag = True
                self.move_drag_position = event.globalPos() - self.pos()
                event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 这里主要设置鼠标放在特定位置时鼠标的图标发生变化
        if QMouseEvent.pos() in self.corner_rect:
            self.setCursor(Qt.SizeFDiagCursor)

        elif QMouseEvent.pos() in self.right_rect:
            self.setCursor(Qt.SizeHorCursor)

        elif QMouseEvent.pos() in self.bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        # 这里就是实现拉伸、拖拽
        if Qt.LeftButton and self.corner_drag:
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())       # 窗口移动的位置
            QMouseEvent.accept()

        elif Qt.LeftButton and self.right_drag:
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()

        elif Qt.LeftButton and self.bottom_drag:
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()

        elif Qt.LeftButton and self.move_drag:
            self.move(QMouseEvent.globalPos() - self.move_drag_position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):       # 鼠标松开，复位所有状态位
        self.corner_drag = False
        self.right_drag = False
        self.bottom_drag = False
        self.move_drag = False

    @QtCore.pyqtSlot()
    def on_CloseButton_clicked(self):       # 关闭窗口操作
        self.timer_date.stop()          # 关闭时间定时器
        self.timer_send.stop()          # 关闭发送定时器
        self.timer_receive.stop()       # 关闭定时器
        self.ser.close()        # 关闭串口
        # shutil.rmtree('images')     # 删除目录及子目录文件
        self.close()        # 关闭窗口

        config['globals'] = {'baudrate': self.SerialBaudRateComboBox.currentText(),     # 将当前的用户数据写入ini文件中，下次使用
                             'stop': self.SerialStopBitsComboBox.currentText(),
                             'data': self.SerialDataBitsComboBox.currentText(),
                             'parity': self.SerialParityComboBox.currentText(),
                             'string': self.SendEdit.toPlainText()}

        with open('setting.ini', 'w') as configfile:        # 打开并写入
            config.write(configfile)

    @QtCore.pyqtSlot()
    def on_MaximizeButton_clicked(self):        # 最大化窗口
        if self.isMaximized():      # 如果窗口已经最大化
            self.showNormal()       # 变为初始时大小
            # 设置正常大小时的图标，具体看效果
            self.MaximizeButton.setStyleSheet("QPushButton{border-image: url(C:/images/maximize_first.png);"
                                              "width: 25px;"
                                              "height:25px}"
                                              "QPushButton:hover{border-image: url(C:/images/maximize_latter.png);}")
        else:
            self.showMaximized()        # 实现窗口最大化
            # 设置最大化时的图标，具体看效果
            self.MaximizeButton.setStyleSheet("QPushButton{border-image: url(C:/images/normal_first.png);"
                                              "width: 15px;"
                                              "height:15px}"
                                              "QPushButton:hover{border-image: url(C:/images/normal_latter.png);}")

    @QtCore.pyqtSlot()
    def on_MinimizeButton_clicked(self):        # 最小化窗口
        self.showMinimized()

    @QtCore.pyqtSlot()
    def on_ClearReceiveButton_clicked(self):        # 清除接收窗口操作
        self.ReceiveEdit.clear()        # 清除接收输出框的数据
        self.receive_num = 0
        self.ReceiveNumlabel.setText('Receive: ' + '{:d}'.format(self.receive_num))     # 清除统计的接收字节数

    @QtCore.pyqtSlot()
    def on_ClearSendButton_clicked(self):       # 清除发送窗口操作
        self.SendEdit.clear()       # 清楚发送输入框的数据
        self.send_num = 0
        self.SendNumlabel.setText('Send: ' + '{:d}'.format(self.send_num))      # 清除统计的发送字节数


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CommAssistant()
    win.show()
    sys.exit(app.exec_())
