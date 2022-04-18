# -*- coding: UTF-8 -*-

import hashlib
import json
import logging
import os
import subprocess
import time

import uiautomator2 as u2

logging.basicConfig(
    format='',
    level=logging.INFO
)

logging = logging.getLogger()


class SpiderBase:
    name = 'base'
    keyword = None
    package_name = None
    prices = [0, 100, 500, 1000, 10000, 300000]
    home_dir = "/Users/beer/temp"
    page_limit = 10

    search_keyword_xpath = None
    search_keyword_confirm_xpath = None
    page_list_xpath = None

    product_choose_xpath = None
    start_price_xpath = None
    end_price_xpath = None
    product_choose_confirm_xpath = None

    def __init__(self, keyword):
        self.keyword = keyword
        self.app = u2.connect()
        self.app.app_start(self.package_name, stop=True)
        logging.info("Init uiautomator2 success，✈️️️")

    def restart(self):
        self.app.app_start(self.package_name, stop=True)

    def get_all_text(self):
        return [_.text.strip() for _ in self.xpath('//android.widget.TextView').all() if _.strip()]

    def get_product_id(self, product_name):
        return hashlib.md5(product_name.encode('utf-8')).hexdigest()

    def sleep(self, seconds):
        time.sleep(seconds)

    def do_search_keyword(self):
        self.xpath(self.search_keyword_xpath).set_text(self.keyword)
        self.sleep(1)
        self.xpath(self.search_keyword_confirm_xpath).click()
        self.app.implicitly_wait(10 * 3)

    def click_sale(self, xpath):
        """
        销量排序
        :param xpath:
        :return:
        """
        self.xpath(xpath).click()
        self.sleep(1)
        self.app.implicitly_wait(10 * 3)

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
        return False

    @staticmethod
    def run_system_cmd(cmd):
        out, error = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
        if error:
            logging.error("run_system_cmd: {}, error: {}".format(cmd, error))
            return False, None
        logging.info("run_system_cmd: {}, success!".format(cmd))
        return True, out.decode('utf-8').strip()

    def return_pre(self):
        """
        返回上一页
        :return:
        """
        self.app.swipe(0, 600, 300, 600, 0.1)
        self.sleep(1)

    def process_page_list(self, start_price, end_price):
        index = 0
        while index < self.page_limit:
            self.sleep(3)
            temp_lists = self.xpath(self.page_list_xpath).all()
            for item in temp_lists:
                if self.pass_item(item):
                    continue
                item.click()
                self.sleep(5)
                self._process_item("{}_{}".format(start_price, end_price))
                self.return_pre()
            index += 1
            # 向下滑动
            self.app.swipe(300, 1000, 300, 400, 0.08)
            self.app.implicitly_wait(10)

    def base_dir(self, price_str: str, product_id: str):
        return self.home_dir + "/{}/{}/{}/{}".format(self.name, self.keyword, price_str, product_id)

    def xpath(self, xpath):
        return self.app.xpath(xpath)

    @staticmethod
    def get_result_path(base_dir):
        return os.path.join(base_dir, 'result.json')

    def save_result(self, base_dir, data):
        with open(self.get_result_path(base_dir), 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        logging.info('🎉🎉🎉 。。。\n')

    def process(self):
        price_len = len(self.prices)
        for index in range(price_len - 1):
            start_price = self.prices[index]
            end_price = self.prices[index + 1] + 1
            self._process_keyword(start_price, end_price)
            self.restart()

    def _process_item(self, price_str):
        pass

    def _process_keyword(self, start_price, end_price):
        pass
