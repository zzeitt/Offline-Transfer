import sys
import cv2
import qrcode
import numpy as np
import pyzbar.pyzbar as pyzbar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QLabel, QPlainTextEdit,
                             QGroupBox, QVBoxLayout,
                             QGridLayout, QDesktopWidget,
                             QApplication)


'''【版本信息】'''
# Author:       zeit
# Version:      1.0
# Date:         19.1.26
# Environment:  Win 10, Python 3.7.0
gui_name = 'Offline Transfer v1'


'''【GUI - Rec】'''


class MyWinRec(QWidget):
    '''【读取摄像头视频类】'''
    class MyVideo():
        def __init__(self, cam):
            self.cam = cam  # 类初始化传入的摄像头，定义为视频类的cam成员变量
            self.frame_cur = np.array([])  # 初始化当前帧为空

        def captureFrame(self):
            ret, frame_read = self.cam.read()
            if (ret == True):
                frame_read = cv2.flip(frame_read, 1, dst=None)  # 水平镜像
                self.frame_cur = cv2.cvtColor(
                    frame_read, cv2.COLOR_BGR2RGB)  # 将opencv的颜色转化为RGB

        def convertFrame(self):
            try:
                h, w = self.frame_cur.shape[:2]
                img = QImage(self.frame_cur, w, h,
                             QImage.Format_RGB888)
                img = QPixmap.fromImage(img)
                return img
            except:
                return None

    '''【二维码识别类】'''
    class MyRecgonize():
        def __init__(self):
            self.qr_data = []  # 二维码识别类的成员变量，存储识别到的数据

        def myDecode(self, img_frame):
            self.qr_decode = pyzbar.decode(img_frame)
            for i in self.qr_decode:
                i = i.data.decode('utf-8')
                self.qr_data.append(i)

    '''GUI - Rec的成员'''

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initWidget()  # 初始化组件
        self.initLayout()  # 初始化布局
        self.initWindow(800, 500)  # 初始化窗口，参数为宽、高
        self.initRecgonize()  # 初始化二维码识别
        self.initVideo()  # 初始化摄像头部分
        # self.show()  # 作为子窗体，构造时就先不show，交由按钮点击信号触发

    def initWidget(self):
        self.lb_cam = QLabel('摄像头载入中……')
        self.pte_qrdata = QPlainTextEdit('未识别到ZBar信息')
        # self.pte_qrdata.setAlignment(Qt.AlignHCenter)  # 设置文本居中
        self.pte_qrdata.setReadOnly(True)  # 该组件设置为只读
        self.pte_qrdata.setEnabled(False)  # 该组件初始化为不可用

    def initLayout(self):
        self.gpbx_cam = QGroupBox('摄像头', self)
        self.gpbx_qrdata = QGroupBox('ZBar内容', self)
        '''箱组布局类型'''
        self.lot_v_cam = QVBoxLayout()
        self.lot_v_qrdata = QVBoxLayout()
        self.lot_v_all = QVBoxLayout()
        '''箱组cam布局设置'''
        self.lot_v_cam.addWidget(
            self.lb_cam, alignment=Qt.AlignHCenter)  # 不加居中可能导致画面扭曲
        self.gpbx_cam.setLayout(self.lot_v_cam)
        '''箱组qrdata布局设置'''
        self.lot_v_qrdata.addWidget(self.pte_qrdata)
        self.gpbx_qrdata.setLayout(self.lot_v_qrdata)
        '''总布局设置'''
        self.lot_v_all.addWidget(self.gpbx_cam)
        self.lot_v_all.addWidget(self.gpbx_qrdata)
        self.setLayout(self.lot_v_all)

    def initWindow(self, w, h):
        '''获取屏幕居中点信息'''
        center_point = QDesktopWidget().availableGeometry().center()
        self.center_point_x = center_point.x()
        self.center_point_y = center_point.y()
        '''窗口初始化'''
        self.setGeometry(0, 0, w, h)
        self.max_w = (self.center_point_x-10)*2  # 窗口允许的最大宽
        self.max_h = (self.center_point_y-20)*2  # 窗口允许的最大高
        self.setMaximumSize(self.max_w, self.max_h)  # 防止窗口尺寸过大
        self.moveToCenter(w, h)
        self.win_name = gui_name + ' - Rec'  # 窗口标题
        self.setWindowTitle(self.win_name)

    def moveToCenter(self, w, h):
        '''窗口过大则先进行调整'''
        if (w > self.max_w) or (h > self.max_h):
            self.adjustSize()
        '''窗口居中'''
        topleft_point_x = (int)(self.center_point_x-w/2)
        topleft_point_y = (int)(self.center_point_y-h/2)
        self.move(topleft_point_x, topleft_point_y)

    def initRecgonize(self):
        self.my_recg = self.MyRecgonize()

    def initVideo(self):
        self.my_cam_video = self.MyVideo(cv2.VideoCapture(0))
        self.my_timer = QTimer(self)
        self.i_frame_count = 0  # 对已加载的视频帧计数
        self.b_need_center = True  # 标志位，标志窗口是否需要居中
        self.my_timer.timeout.connect(self.showVideoFrame)
        self.my_timer.start(100)  # 设置刷新时间为100毫秒

    def showVideoFrame(self):
        try:
            self.my_cam_video.captureFrame()
            self.lb_cam.setPixmap(self.my_cam_video.convertFrame())
            self.lb_cam.setScaledContents(True)  # 视频帧缩放填充
            '''下面的if嵌套部分用于实现居中一次的功能'''
            if self.b_need_center:
                if self.i_frame_count < 1:
                    self.i_frame_count += 1
                else:
                    w = self.width()
                    h = self.height()
                    self.moveToCenter(w, h)
                    self.b_need_center = False
            '''顺带进行二维码识别'''
            self.my_recg.myDecode(self.my_cam_video.frame_cur)
            if (len(self.my_recg.qr_data) > 0):
                self.pte_qrdata.setEnabled(True)
                self.pte_qrdata.setPlainText(self.my_recg.qr_data[0])
                self.my_timer.stop()  # 识别成功则叫停
        except TypeError:
            print('No Frame!')


'''【GUI - Gen】'''


class MyWinGen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initWidget()  # 初始化组件
        self.initLayout()  # 初始化布局
        self.initWindow(800, 740)  # 初始化窗口，参数为宽、高
        # self.show()  # 作为子窗体，构造时就先不show，交由按钮点击信号触发

    def initWidget(self):
        '''文本框控件'''
        self.pte_qrdata = QPlainTextEdit()
        '''清空按钮控件'''
        self.bt_clear = QPushButton('清空')
        self.bt_clear.clicked.connect(self.pte_qrdata.clear)  # 链接清空文本的函数
        '''确认按钮控件'''
        self.bt_ok = QPushButton('确认')
        self.bt_ok.clicked.connect(self.data2QRCode)  # 链接确认文本的函数
        '''二维码显示控件'''
        self.lb_qrimg = QLabel('将文本粘贴至上方\n\n点击「确认」按钮，进行二维码转化。')
        self.lb_qrimg.setAlignment(Qt.AlignCenter)

    def initLayout(self):
        '''箱组声明'''
        self.gpbx_qrdata = QGroupBox('文本', self)
        self.gpbx_qrimg = QGroupBox('二维码', self)
        '''箱组布局类型'''
        self.lot_g_qrdata = QGridLayout()
        self.lot_v_qrimg = QVBoxLayout()
        self.lot_v_all = QVBoxLayout()
        '''箱组qrdata布局设置'''
        self.lot_g_qrdata.addWidget(self.pte_qrdata, 0, 0, 5, 8)  # 文本编辑框占4行8列
        self.lot_g_qrdata.addWidget(self.bt_clear, 1, 8)
        self.lot_g_qrdata.addWidget(self.bt_ok, 3, 8)
        self.gpbx_qrdata.setLayout(self.lot_g_qrdata)
        '''箱组qrimg布局设置'''
        self.lot_v_qrimg.addWidget(self.lb_qrimg, alignment=Qt.AlignHCenter)
        self.gpbx_qrimg.setLayout(self.lot_v_qrimg)
        '''总布局设置'''
        self.lot_v_all.addWidget(self.gpbx_qrdata)
        self.lot_v_all.addWidget(self.gpbx_qrimg)
        self.setLayout(self.lot_v_all)

    def initWindow(self, w, h):
        '''获取屏幕居中点信息'''
        center_point = QDesktopWidget().availableGeometry().center()
        self.center_point_x = center_point.x()
        self.center_point_y = center_point.y()
        '''窗口初始化'''
        self.setGeometry(0, 0, w, h)
        self.max_w = (self.center_point_x-10)*2  # 窗口允许的最大宽
        self.max_h = (self.center_point_y-20)*2  # 窗口允许的最大高
        self.setMaximumSize(self.max_w, self.max_h)  # 防止窗口尺寸过大
        self.moveToCenter(w, h)
        self.win_name = gui_name + ' - Gen'  # 窗口标题
        self.setWindowTitle(self.win_name)

    def moveToCenter(self, w, h):
        '''窗口过大则先进行调整'''
        if (w > self.max_w) or (h > self.max_h):
            self.adjustSize()
        '''窗口居中'''
        topleft_point_x = (int)(self.center_point_x-w/2)
        topleft_point_y = (int)(self.center_point_y-h/2)
        self.move(topleft_point_x, topleft_point_y)

    def data2QRCode(self):
        try:
            self.qr_data = self.pte_qrdata.toPlainText()  # 获取输入框文本
            '''调用qrcode库生成二维码'''
            self.qr_img_pil = qrcode.make(self.qr_data)
            self.qr_img_pixmap = self.qr_img_pil.toqpixmap()  # 生成QPixmap图片
            self.qr_img_pixmap = self.qr_img_pixmap.scaled(
                800, 500, Qt.KeepAspectRatio,
                Qt.SmoothTransformation)  # 设置QPixmap自适应
            self.lb_qrimg.setPixmap(self.qr_img_pixmap)
            '''窗口居中'''
            w = self.width()            # 由于无法生成二维码需要时间，左边函数
            h = self.height()           # 获取的宽高其实是初始值，所以这里就采
            self.moveToCenter(w, h)     # 用固定图片框的大小的方案了
        except qrcode.exceptions.DataOverflowError:
            self.lb_qrimg.setText(
                '<font color=red>\
                <b>⚠ WARNING ⚠</b><br /><br />\
                输入的数据量太大啦<br /><br />\
                ::＞﹏＜::</font>')
            self.lb_qrimg.adjustSize()


'''【GUI - All】'''


class MyWinAll(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initWidget()  # 初始化组件
        self.initLayout()  # 初始化布局
        self.initWindow(500, 300)  # 初始化窗体，参数为宽、高
        self.show()

    def initWidget(self):
        '''展示部分'''
        self.lb_welcom = QLabel(
            '<h3>ʚ(●ˇ∀ˇ●)ɞ</h3>\
            <br />\
            <p>Words are powerful</p>\
            <p>no one can stop them</p>\
            <p>even WiFi...</p>')
        self.lb_welcom.setAlignment(Qt.AlignCenter)
        '''识别按钮'''
        self.bt_rec = QPushButton('识别')
        self.bt_rec.clicked.connect(self.initRecWin)
        '''生成按钮'''
        self.bt_gen = QPushButton('生成')
        self.bt_gen.clicked.connect(self.initGenWin)

    def initLayout(self):
        '''布局类型'''
        self.lot_g_all = QGridLayout()
        '''总布局设置'''
        self.lot_g_all.addWidget(self.lb_welcom, 0, 0, 2, 7)  # 展示框占4行7列
        self.lot_g_all.addWidget(self.bt_rec, 2, 1, 1, 1)
        self.lot_g_all.addWidget(self.bt_gen, 2, 5, 1, 1)
        self.setLayout(self.lot_g_all)

    def initWindow(self, w, h):
        '''获取屏幕居中点信息'''
        center_point = QDesktopWidget().availableGeometry().center()
        self.center_point_x = center_point.x()
        self.center_point_y = center_point.y()
        '''窗口初始化'''
        self.setGeometry(0, 0, w, h)
        self.max_w = (self.center_point_x-10)*2  # 窗口允许的最大宽
        self.max_h = (self.center_point_y-20)*2  # 窗口允许的最大高
        self.setMaximumSize(self.max_w, self.max_h)  # 防止窗口尺寸过大
        self.moveToCenter(w, h)
        self.win_name = gui_name
        self.setWindowTitle(self.win_name)

    def moveToCenter(self, w, h):
        '''窗口过大则先进行调整'''
        if (w > self.max_w) or (h > self.max_h):
            self.adjustSize()
        '''窗口居中'''
        topleft_point_x = (int)(self.center_point_x-w/2)
        topleft_point_y = (int)(self.center_point_y-h/2)
        self.move(topleft_point_x, topleft_point_y)

    def initRecWin(self):
        '''识别窗口的生成调用函数'''
        self.win_rec = MyWinRec()
        self.win_rec.show()

    def initGenWin(self):
        '''生成窗口的生成调用函数'''
        self.win_gen = MyWinGen()
        self.win_gen.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui_all = MyWinAll()
    sys.exit(app.exec_())
