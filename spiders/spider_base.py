# -*- coding: UTF-8 -*-

import hashlib
import json
import logging
import os
import random
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime

import uiautomator2 as u2

home_dir = os.path.join(os.path.expanduser('~'), "uiautomator_spider")
if not os.path.exists(home_dir):
    os.makedirs(home_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO
)

log = logging.getLogger()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
filename = datetime.now().strftime('%Y-%m-%d')
file_handler = logging.FileHandler("{}/{}.log".format(home_dir, filename))
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


class SpiderBase:
    name = 'base'
    keyword = None
    package_name = None
    activity = None
    prices = [0, 100, 500, 1000, 10000, 300000]
    item_limit = 80

    cached_item = 0  # 提前退出条件，没达到 item_limit 的限制下

    search_keyword_xpath = None
    search_keyword_confirm_xpath = None
    page_list_xpath = None

    product_choose_xpath = None
    start_price_xpath = None
    end_price_xpath = None
    product_choose_confirm_xpath = None
    watchers = [

    ]

    stop = True

    def __init__(self, keyword):
        self.keyword = keyword
        self._index = 1
        try:
            self.app = u2.connect()
        except:
            log.info("Can't find any android device. exit")
            sys.exit(-1)

        self.restart()
        log.info("Init uiautomator2 success，✈️️️")
        for watcher in self.watchers:
            self.app.watcher.when(watcher).click()

    def restart(self):
        self.app.app_start(self.package_name, stop=True, activity=self.activity)
        self.sleep(20)  # 等待 app 重启，取决于设备性能，设置久一点

    @staticmethod
    def _error(msg):
        log.error(msg)
        sys.exit()

    @staticmethod
    def uuid():
        return str(uuid.uuid4())

    def screen_debug(self):
        file_name = os.path.join(home_dir, self.uuid() + '.png')
        self.app.screenshot(file_name)
        log.info("debug: {}".format(file_name))
        return file_name

    @staticmethod
    def get_image_size(texts):
        for _ in texts:
            z = re.match("^[1-9]\d*\/[1-9]\d*$", str(_))
            if z:
                return int(z.group().split('/')[-1])
        return 1

    def get_all_text(self, xpath=None):
        if not xpath:
            xpath = '//android.widget.TextView'
        return [_.text.strip() for _ in self.xpath(xpath).all() if _.text.strip()]

    @staticmethod
    def get_product_id(product_name):
        return hashlib.md5(product_name.encode('utf-8')).hexdigest()

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)

    @staticmethod
    def sleep_random(start=None, end=None):
        if not start:
            start = 1
        if not end:
            end = 5
        time.sleep(random.randint(start, end))

    def do_search_keyword(self):
        log.info("set text: {}".format(self.keyword))
        self.xpath(self.search_keyword_xpath).set_text(self.keyword)
        self.xpath(self.search_keyword_confirm_xpath).click()

    def click_sale(self, xpath):
        """
        销量排序
        :param xpath:
        :return:
        """
        log.info("click sale desc ....")
        self.xpath(xpath).click()

    def range_price(self, start_price, end_price):
        # 展开 筛选 操作
        self.xpath(self.product_choose_xpath).click()

        # 输入 【start_price， end_price】
        self.xpath(self.start_price_xpath).set_text(str(start_price))
        self.sleep(3)
        self.xpath(self.end_price_xpath).set_text(str(end_price))

        # https://www.cnblogs.com/yoyoketang/p/10850591.html 隐藏键盘
        self.app.press(4)

        # 确认按钮
        self.xpath(self.product_choose_confirm_xpath).click()

    def pass_item(self, item):
        y = item.rect[1]
        if y < 300:
            logging.info("可能是隐藏在其他文本下面，跳过")
            return True
        return False

    @staticmethod
    def run_system_cmd(cmd):
        out, error = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
        if error:
            log.error("run_system_cmd: {}, error: {}".format(cmd, error))
            return False, None
        log.info("run_system_cmd: {}, success!".format(cmd))
        return True, out.decode('utf-8').strip()

    def return_pre(self, times=1):
        """
        返回上一页
        :return:
        """
        for i in range(times):
            self.swipe_right()

    def swipe_left(self):
        """
        左滑
        :return:
        """
        self.app.swipe(600, 600, 0, 600, 0.08)
        self.sleep_random()

    def swipe_down(self):
        """
        下滑
        :return:
        """
        self.app.swipe(300, 1000, 300, 400, 0.08)
        self.sleep_random()

    def swipe_right(self):
        """
        右滑
        :return:
        """
        self.sleep(1.5)
        self.app.swipe(0, 600, 300, 600, 0.1)
        self.sleep(1.5)

    def process_page_list(self, start_price, end_price):
        while self._index < self.item_limit:
            log.info("cached_item: {}".format(self.cached_item))
            temp_lists = self.xpath(self.page_list_xpath).all()
            if not temp_lists:
                return
            for item in temp_lists:
                if self.pass_item(item):
                    continue

                click_before = len(self.get_all_text())
                item.click()
                click_after = len(self.get_all_text())
                if click_before == click_after:
                    logging.info('点击跳转失败，skip')
                    continue

                self.sleep(5)
                log.info('start process new item.....')
                if start_price and end_price:
                    self._process_item("{}_{}".format(start_price, end_price))
                else:
                    self._process_item(None)
                # 不是列表页再返回
                if not self.xpath(self.page_list_xpath).all():
                    self.return_pre()

                if self.cached_item > 20:
                    return
                    # 向下滑动
            self.app.swipe(300, 1000, 300, 400, 0.08)

    def base_dir(self, sub_dir, product_id):
        if sub_dir:
            result = home_dir + "/{}/{}/{}/{}".format(self.name, self.keyword, sub_dir, product_id)
        else:
            result = home_dir + "/{}/{}/{}".format(self.name, self.keyword, product_id)
        os.makedirs(result, exist_ok=True)
        return result

    def get_current_count(self, sub_dir=None):
        if sub_dir:
            dir_path = home_dir + "/{}/{}/{}".format(self.name, self.keyword, sub_dir)
        else:
            dir_path = home_dir + "/{}/{}".format(self.name, self.keyword)
        if os.path.exists(dir_path):
            return len(os.listdir(dir_path))
        return -1

    def xpath(self, xpath):
        return self.app.xpath(xpath)

    def xpaths(self, xpaths):
        for _xpath in xpaths:
            elm = self.xpath(_xpath)
            if elm.exists:
                return elm

    def xpath_text(self, xpath):
        elm = self.app.xpath(xpath)
        self.sleep(1)
        if elm.exists:
            return elm.text

    def xpath_text_by_swipe(self, xpath):
        elm = self.xpath(xpath)
        index = 0
        while not elm.exists:
            index = index + 1
            # 往下滑动
            self.app.swipe(300, 800, 300, 400, 0.1)
            elm = self.xpath(xpath)
            if index > 10:
                return ''
            log.info(f"swipe index {index} ...")
        return elm.text

    @staticmethod
    def get_result_path(base_dir):
        return os.path.join(base_dir, 'result.json')

    def save_result(self, base_dir, data):
        data['_index'] = self._index
        data['ts'] = int(time.time())
        with open(self.get_result_path(base_dir), 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        log.info('🎉🎉🎉 。。。\n')
        self._index += 1
        self.sleep_random(10, 20)
        if self.cached_item > 0:
            self.cached_item -= 1

    def process(self):
        if self.prices:
            for index in range(len(self.prices) - 1):
                start_price = self.prices[index]
                end_price = self.prices[index + 1] + 1
                self._process_keyword(start_price, end_price)
                self.restart()
        else:
            self._process_keyword('', '')
            self.restart()

    def _process_item(self, price_str):
        pass

    def _process_keyword(self, start_price, end_price):
        pass
