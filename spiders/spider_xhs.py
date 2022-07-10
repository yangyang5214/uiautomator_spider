# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, log as logging

"""
穿戴甲  美甲 美甲片
"""

like_xpath = '//*[@resource-id="com.xingin.xhs:id/dzk"]'
collect_xpath = '//*[@resource-id="com.xingin.xhs:id/dyg"]'
comment_xpath = '//*[@resource-id="com.xingin.xhs:id/dym"]'
page_list_xpath = '//*[@resource-id="com.xingin.xhs:id/dcy"]/android.widget.FrameLayout//android.view.View'
search_input_xpath = '//*[@resource-id="com.xingin.xhs:id/f20"]'
search_text_xpath = '//*[@resource-id="com.xingin.xhs:id/ddd"]'
search_click = '//*[@resource-id="com.xingin.xhs:id/ddh"]'


class SpiderXhs(SpiderBase):
    name = "xhs"
    package_name = 'com.xingin.xhs'

    page_list_xpath = page_list_xpath

    watchers = [
        '//*[@resource-id="com.xingin.xhs:id/d8w"]'
    ]

    # 三种排序方式：
    sort_items = [
        # ['最新', '//*[@resource-id="com.xingin.xhs:id/dcy"]/android.view.ViewGroup[1]/android.widget.TextView[3]'],
        ['最热', '//*[@resource-id="com.xingin.xhs:id/dcy"]/android.view.ViewGroup[1]/android.widget.TextView[2]'],
        ['综合', '//*[@resource-id="com.xingin.xhs:id/dcy"]/android.view.ViewGroup[1]/android.widget.TextView[1]'],
    ]

    blacklist = [
        "教程",
    ]

    skip_count = 0

    item_limit = 100
    skip_flag = 3  # 出现多少次 就多滑动几页
    swipe_flag = 1  # 下滑多少次

    def process(self):
        for item in self.sort_items:
            sort_key, sort_xpath = item[0], item[1]
            logging.info("start process: {} - {}".format(self.keyword, sort_key))
            self._process_keyword(sort_key, sort_xpath)
            self.restart()

    def _process_keyword(self, sort_key, sort_xpath):
        self.xpath(search_input_xpath).click()
        self.xpath(search_text_xpath).set_text(self.keyword)
        self.xpath(search_click).click()

        self.sleep_random(10, 20)  # 筛选后 等待页面加载

        self.xpath(sort_xpath).click()

        self.sleep_random(10, 20)  # 排序后 等待页面加载

        logging.info("click 图文。。。")

        # 筛选图文
        tu_wen = self.xpath('//*[@resource-id="com.xingin.xhs:id/dcy"]/android.view.ViewGroup[1]/android.widget.LinearLayout[2]/android.widget.TextView[1]')
        if tu_wen.exists:
            tu_wen.click()
            self.sleep_random(10, 20)
        else:
            logging.info("点击 **筛选 图文** 出错")
            exit()

        self.process_page_list(sort_key, None)

    def process_page_list(self, sort_key, _):
        flag = True
        while flag:
            current_count = self.get_current_count(sort_key)
            logging.info(f"current_count: {current_count}")
            if current_count > self.item_limit:
                break

            temp_lists = self.xpath(self.page_list_xpath).all()
            pre_len = len(temp_lists)
            for item in temp_lists:
                if self.pass_item(item):
                    continue
                logging.info('start process new item.....index: {}'.format(self._index))

                item.click()
                r = self._process_item(sort_key)
                if r and r == -1:
                    flag = False
                    break

                while True:
                    current_len = len(self.app.xpath(self.page_list_xpath).all())
                    if current_len == 0:  # 只要没回到列表页，就再次返回 pre_len 会变
                        logging.info(f"current {current_len} , pre: {pre_len}, try return pre ...")
                        self.return_pre()
                        self.sleep(5)
                    else:
                        break
            self.swipe_down()
            self.sleep(10)  # 控制速率

            if self.skip_count >= self.skip_flag:
                for _ in range(self.swipe_flag):
                    self.swipe_down()
                    self.sleep(2)
                self.skip_count = 0  # 重置为 0

    def get_auth_info(self):
        logging.info("开始获取个人信息。。。start")
        # 点击头像进入个人主页
        avatar_layout = self.xpath('//*[@resource-id="com.xingin.xhs:id/avatarLayout"]')
        if avatar_layout.exists:
            avatar_layout.click()
            self.sleep_random()
        else:
            return {}
        extra_info = self.get_all_text('//*[@resource-id="com.xingin.xhs:id/bf_"]')
        data = {
            'nickname': self.xpath_text('//*[@resource-id="com.xingin.xhs:id/eek"]'),
            '_id': self.xpath_text('//*[@resource-id="com.xingin.xhs:id/eel"]'),
            "geo_info": self.xpath_text('//*[@resource-id="com.xingin.xhs:id/eei"]'),
            'tag_info': self.get_all_text('//*[@resource-id="com.xingin.xhs:id/djc"]'),
            'extra_info': extra_info
        }
        self.return_pre()
        logging.info("开始获取个人信息。。。end")
        return data

    def _process_item(self, price_str):
        logging.info("start process_item ...")
        self.sleep_random()

        buk = self.xpath('//*[@resource-id="com.xingin.xhs:id/c_c"]')
        if not buk.exists or not buk.text.startswith('说点什么'):
            logging.error("可能是 视频内容 skip")
            return -1

        title = self.xpath_text('//*[@resource-id="com.xingin.xhs:id/e04"]')
        if not title:
            logging.error("获取 title 失败, skip {}".format(self.screen_debug()))
            return

        like_count = self.xpath_text(like_xpath)
        collect_count = self.xpath_text(collect_xpath)
        comment_count = self.xpath_text(comment_xpath)

        product_id = self.get_product_id(title)
        base_dir = self.base_dir(price_str, product_id)
        logging.info("result: {}".format(base_dir))
        self.app.screenshot(os.path.join(base_dir, 'main.jpg'))

        if os.path.exists(self.get_result_path(base_dir)):
            logging.info("cache... skip\n")
            self.skip_count += 1
            return

        image_size = 1
        image_xpath = self.xpath('//*[@resource-id="com.xingin.xhs:id/noteContentLayout"]/android.widget.LinearLayout[1]/android.widget.ImageView')
        if image_xpath.exists:
            image_size = len(image_xpath.all())

        for index in range(image_size):
            image_elm = self.xpath('//*[@resource-id="com.xingin.xhs:id/noteContentLayout"]/android.widget.FrameLayout[1]')
            image_name = os.path.join(base_dir, '{}.jpg'.format(index))
            if image_elm.exists:
                image_elm.screenshot().save(image_name)
            if index != image_size - 1:
                self.swipe_left()

        logging.info("image save end ...")

        # 不能放在前面，需要 swipe 获取
        content = self.xpath_text_by_swipe('//*[@resource-id="com.xingin.xhs:id/c79"]')
        if not content:
            logging.info("获取 content 失败, skip {}".format(self.screen_debug()))

        last_update = self.xpath_text_by_swipe('//*[@resource-id="com.xingin.xhs:id/dzt"]')
        # auth_info = self.get_auth_info()
        data = {
            'title': title,
            'content': content,
            'last_update': last_update,
            'comment_count': comment_count,
            'like_count': like_count,
            'collect_count': collect_count,
            'auth_info': {}
        }
        self.save_result(base_dir, data)
