# -*- coding: UTF-8 -*-
import argparse
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtWidgets import QPushButton

from spiders.spider_base import SpiderBase, u2
from spiders.spider_base import log as logging

version = '0.0.1'


class SpiderWindow(QMainWindow):
    def __init__(self, all_spiders):
        QMainWindow.__init__(self)
        self.resize(600, 200)
        self.setWindowTitle("uiautomator_spider({})".format(version))

        self.keyword_label = QLabel(self)
        self.keyword_label.setText("平台: ")
        self.keyword_label.move(20, 20)

        self.cb = QComboBox(self)
        self.all_spiders = all_spiders
        self.cb.addItems(self.all_spiders)
        self.cb.currentIndexChanged[int].connect(self.selected)
        self.cb.move(50, 25)
        self.cb.resize(100, 30)

        self.keyword_label = QLabel(self)
        self.keyword_label.setText("关键词: ")
        self.keyword_label.move(200, 20)

        self.keyword_line = QLineEdit(self)
        self.keyword_line.resize(300, 30)
        self.keyword_line.move(250, 15)

        self.btn_run = QPushButton('run', self)
        self.btn_run.clicked.connect(self.run)
        self.btn_run.resize(80, 40)
        self.btn_run.move(300, 100)
        self.current_spider = self.all_spiders[0]

    def selected(self, index):
        self.current_spider = self.all_spiders[index]

    def run(self):
        text = self.keyword_line.text()
        all_text = [_ for _ in text.split(" ") if _.strip()]
        if not all_text:
            QMessageBox.critical(self, "⚠️", "请输入关键词")
        else:
            try:
                u2.connect()
            except:
                QMessageBox.critical(self, "⚠️", "未检测到手机设备")
                return
            logging.info("spider: {}, keyword: {}".format(self.current_spider, all_text))
            for k in all_text:
                main(spider_map.get(self.current_spider, SpiderBase)(k))


def main(spider: SpiderBase):
    spider.process()


if __name__ == '__main__':
    spider_map = {}
    for sub in SpiderBase.__subclasses__():
        spider_map[sub.name] = sub

    if len(sys.argv) != 1:
        parser = argparse.ArgumentParser(description='Collect some data by spider...')
        parser.add_argument('-n', '--name', help='spider name...', choices=spider_map.keys())
        parser.add_argument('-k', '--keyword', help='spider keyword... eg: 项链', required=False)
        args = parser.parse_args()
        main(spider_map.get(args.name, SpiderBase)(args.keyword))
    else:
        app = QtWidgets.QApplication(sys.argv)
        spider_window = SpiderWindow(list(spider_map.keys()))
        spider_window.show()
        sys.exit(app.exec_())
