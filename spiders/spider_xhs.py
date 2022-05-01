# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, logging

"""
穿戴甲  美甲 美甲片
"""


class SpiderXhs(SpiderBase):
    name = "xhs"
    package_name = 'com.xingin.xhs'

    page_list_xpath = '//*[@resource-id="com.xingin.xhs:id/csn"]/android.widget.FrameLayout'

    # 三种排序方式：
    sort_items = {
        '综合': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[1]',
        '最热': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[2]',
        '最新': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[3]',
    }

    page_limit = 20

    def process(self):
        for sort_key, sort_xpath in self.sort_items.items():
            logging.info("start process: {} - {}".format(self.keyword, sort_key))
            self._process_keyword(sort_key, sort_xpath)
            self.restart()

    def _process_keyword(self, sort_key, sort_xpath):
        # search btn
        self.xpath('//*[@resource-id="com.xingin.xhs:id/ebt"]').click()
        # 输入 keyword
        self.xpath('//*[@resource-id="com.xingin.xhs:id/ct1"]').set_text(self.keyword)
        # 触发搜索
        self.xpath('//*[@resource-id="com.xingin.xhs:id/ct4"]').click()

        self.xpath(sort_xpath).click()
        self.process_page_list(sort_key, None)

    def process_page_list(self, sort_key, _):
        index = 0
        while index < self.page_limit:
            temp_lists = self.xpath(self.page_list_xpath).all()
            for item in temp_lists:
                item.click()
                self.sleep(5)
                logging.info('start process new item.....')
                if self._process_item(sort_key):
                    self.return_pre()
            index += 1
            self.swipe_down()

    def _process_item(self, price_str):
        title = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dcg"]')
        if not title:
            for item in self.get_all_text():
                if '发弹幕' == item:
                    logging.info("是个视频内容, skip")
                    return True
            return False

        product_id = self.get_product_id(title)
        base_dir = self.base_dir(price_str, product_id)
        logging.info("result: {}".format(base_dir))
        self.app.screenshot(os.path.join(base_dir, 'main.png'))

        nickname = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/nickNameTV"]')
        like_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dbt"]')
        collect_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dam"]')
        comment_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/das"]')

        if os.path.exists(self.get_result_path(base_dir)):
            logging.info("cache... skip\n")
            return True

        image_size = 1
        image_xpath = self.xpath('//*[@resource-id="com.xingin.xhs:id/noteContentLayout"]/android.widget.LinearLayout[1]/android.widget.ImageView')
        if image_xpath.exists:
            image_size = len(image_xpath.all())

        for index in range(image_size):
            image_elm = self.xpath('//*[@resource-id="com.xingin.xhs:id/noteContentLayout"]/android.widget.FrameLayout[1]')
            image_name = os.path.join(base_dir, '{}.png'.format(index))
            if image_elm.exists:
                image_elm.screenshot().save(image_name)
            self.swipe_left()

        content = self.xpath_text_by_swipe('//*[@resource-id="com.xingin.xhs:id/brq"]')
        last_update = self.xpath_text_by_swipe('//*[@resource-id="com.xingin.xhs:id/dc2"]')

        data = {
            'nickname': nickname,
            'title': title,
            'content': content,
            'last_update': last_update,
            'comment_count': comment_count,
            'like_count': like_count,
            'collect_count': collect_count,
        }
        self.save_result(base_dir, data)
        return True
