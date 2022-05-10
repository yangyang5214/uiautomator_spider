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
        'zong_he': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[1]',
        'zui_re': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[2]',
        'zui_xin': '//*[@resource-id="com.xingin.xhs:id/csn"]/android.view.ViewGroup[1]/android.widget.TextView[3]',
    }

    page_limit = 60

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

    def get_auth_info(self):
        avatar_layout = self.xpath('//*[@resource-id="com.xingin.xhs:id/avatarLayout"]')
        if avatar_layout.exists:
            avatar_layout.click()
        else:
            return {}
        cyq = self.get_all_text('//*[@resource-id="com.xingin.xhs:id/cyq"]/android.view.ViewGroup[3]//*')
        extra_info = []
        if cyq:
            extra_info = cyq[:6]  # 关注/粉丝/点赞
        data = {
            'nickname': self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dqs"]'),
            '_id': self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dqt"]'),
            'desc': self.xpath_text('//*[@resource-id="com.xingin.xhs:id/fih"]'),
            'tag_info': self.get_all_text('//*[@resource-id="com.xingin.xhs:id/cyh"]//*'),
            'extra_info': extra_info
        }
        self.return_pre()
        return data

    def _process_item(self, price_str):
        title = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dcg"]')
        if not title:
            for item in self.get_all_text():
                if '发弹幕' == item:
                    logging.info("是个视频内容, skip")
                    return True
            return False

        like_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dbt"]')
        if not like_count:
            logging.info("可能是个广告内容, skip")
            return True

        collect_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/dam"]')
        comment_count = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/das"]')

        product_id = self.get_product_id(title)
        base_dir = self.base_dir(price_str, product_id)
        logging.info("result: {}".format(base_dir))
        self.app.screenshot(os.path.join(base_dir, 'main.png'))

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
            'title': title,
            'content': content,
            'last_update': last_update,
            'comment_count': comment_count,
            'like_count': like_count,
            'collect_count': collect_count,
            'auth_info': self.get_auth_info(),
        }
        self.save_result(base_dir, data)
        return True
