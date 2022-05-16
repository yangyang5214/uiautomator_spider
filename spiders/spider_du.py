# -*- coding: UTF-8 -*-
import os
import random
import re

from spiders.spider_base import SpiderBase, log

"""
du spider
"""


class SpiderDu(SpiderBase):
    name = "du"
    package_name = 'com.shizhuang.duapp'
    page_list_xpath = '//*[@resource-id="com.shizhuang.duapp:id/recyclerView"]/android.view.ViewGroup'
    item_limit = 80

    watchers = [
        '//*[@resource-id="com.shizhuang.duapp:id/iv_close"]'
    ]

    prices = [100, 1000]

    def __init__(self, keyword):
        super().__init__(keyword)

    def _process_keyword(self, start_price, end_price):
        log.info("尝试点击购买标签")
        rbtn_mall = self.xpaths([
            '//*[@resource-id="com.shizhuang.duapp:id/rbtn_mall"]',
            '//*[@resource-id="com.shizhuang.duapp:id/tab_mall"]'
        ])
        if rbtn_mall.exists:
            rbtn_mall.click()
        else:
            self._error("Can't find rbtn_mall, exit. {}'".format(self.screen_debug()))

        log.info("尝试输入关键词: {}".format(self.keyword))
        search = self.xpath('//*[@resource-id="com.shizhuang.duapp:id/fvSearch"]')
        keyword_search = self.xpath('//*[@resource-id="com.shizhuang.duapp:id/laySearchContent"]')
        if search.exists:
            search.set_text(self.keyword)
        elif keyword_search.exists:
            keyword_search.set_text(self.keyword)

        self.sleep(1)

        log.info("点击【搜索】按钮")
        self.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvComplete"]').click()

        log.info("点击【销量】排序按钮")
        self.xpath('//*[@text="累计销量"]').click()

        if start_price:
            log.info("展开 【筛选】 操作")
            self.xpath('//*[@text="筛选"]').click()
            log.info("输入 【start_price:{}】【end_price:{}】".format(start_price, end_price))
            self.xpath(
                '//*[@resource-id="com.shizhuang.duapp:id/layMenuFilterView"]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]') \
                .set_text(str(start_price))
            self.sleep(random.random() * 3)
            self.xpath(
                '//*[@resource-id="com.shizhuang.duapp:id/layMenuFilterView"]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]') \
                .set_text(str(end_price))

            # https://www.cnblogs.com/yoyoketang/p/10850591.html 隐藏键盘
            self.app.press(4)

            # 确认按钮
            self.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvConfirm"]').click()

        self.process_page_list(start_price, end_price)

    def _process_item(self, price_str: str):
        log.info('start process new item.....')

        all_text = self.xpath('//android.widget.TextView').all()
        all_texts = [_.text.strip() for _ in all_text]
        sales = None
        prices = []
        image_size = 0
        image_size_start = 0

        max_length = -1
        product_name = None
        for text in all_texts:
            if len(text) > max_length:
                max_length = len(text)
                product_name = text  # 取最长的作为 product_name

            # 都是 1/6 1/5 之类的
            if not image_size and re.match('^\d+/\d+$', text):
                arr = text.split('/')
                image_size_start = int(arr[0])
                image_size = int(arr[1])
            elif text.startswith('¥'):
                prices.append(text)
            elif '付款' in text and '想要' in text:
                sales = text

        if not prices and not image_size:
            # 提前结束
            self.screen_debug()
            exit()

        product_id = None
        if product_name:
            product_id = self.get_product_id(product_name + str(prices))  # 以 product_name + price 确定唯一性
        else:
            self.screen_debug()
            exit()

        base_dir = self.base_dir(price_str, product_id)
        result_path = SpiderBase.get_result_path(base_dir)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        else:
            if os.path.exists(result_path):
                log.info('hit cache ... skip')
                self.cached_item += 1
                return

        self.app.screenshot(os.path.join(base_dir, 'main.png'))

        log.info('开始处理图片。。。image_size: {}'.format(image_size))

        image_name = os.path.join(base_dir, 'main.png')
        self.app.screenshot(image_name)

        for i in range(image_size_start, image_size):
            self.swipe_left()
            image_name = os.path.join(base_dir, str(i - image_size_start) + '.png')
            elm = self.xpath('//*[@resource-id="com.shizhuang.duapp:id/pullLayout"]//android.widget.ImageView')
            if elm.exists:
                elm.screenshot().save(image_name)
            else:
                self.screen_debug()
                exit()

        data = {
            'product_id': product_id,
            'price': prices[0],
            'original_price': prices[1] if len(prices) > 1 else prices[0],
            'product_name': product_name,
            'sales': sales,
        }
        self.save_result(base_dir, data)
