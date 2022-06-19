# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, log as logging

"""
du spider
"""


class SpiderIns(SpiderBase):
    name = "ins"
    package_name = 'com.instagram.android'

    page_list_xpath = 'com.instagram.android:id/image_button'

    page_limit = 10  # 滑动多少页

    def _process_keyword(self, start_price, end_price):
        # search btn
        self.xpath('//*[@resource-id="com.instagram.android:id/search_tab"]/android.widget.ImageView[1]').click()

        self.sleep(5)

        # 输入 keyword
        self.xpath('//*[@resource-id="com.instagram.android:id/action_bar_search_hints_text_layout"]').set_text(self.keyword)

        # 查看全部结果
        self.xpath('//*[@resource-id="com.instagram.android:id/echo_text"]').click()

        # 切换到标签
        # self.xpath('//*[@content-desc="标签"]').click()
        # self.sleep(5)

        # 选择第一个
        # self.xpath('//*[@resource-id="com.instagram.android:id/recycler_view"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').click()

        self.sleep(5)

        self.process_page_list(start_price, end_price)

    def pass_item(self, item):
        return False

    def process_page_list(self, start_price, end_price):
        index = 0
        while index < self.page_limit:
            temp_lists = self.xpath(self.page_list_xpath).all()
            for item in temp_lists:
                if self.pass_item(item):
                    continue
                item.click()
                self.sleep(3)
                logging.info('start process new item.....')
                if self._process_item(''):
                    self.return_pre()
            index += 1
            self.swipe_down()

    def _process_item(self, price_str: str):

        like_num = ''
        for item in self.get_all_text():
            if '次赞' in item:
                like_num = item
                break

        comment_num = self.xpath_text('//*[@resource-id="com.instagram.android:id/row_feed_view_all_comments_text"]')

        profile_name = self.xpath_text('//*[@resource-id="com.instagram.android:id/row_feed_photo_profile_name"]')
        if not profile_name:
            logging.info("不是详情页，skip 😭😭😭")
            return

        content = self.xpath_text_by_swipe('//*[@resource-id="com.instagram.android:id/row_feed_comment_textview_layout"]/android.widget.Button[2]')
        logging.info("content: {}".format(content))

        product_id = self.get_product_id(profile_name + content)
        base_dir = self.base_dir(price_str, product_id)
        if os.path.exists(self.get_result_path(base_dir)):
            logging.info("cache... skip\n")
            return True

        image_xpaths = [
            '//*[@resource-id="com.instagram.android:id/carousel_media_group"]',
            '//*[@resource-id="com.instagram.android:id/zoomable_view_container"]'
        ]

        self.app.screenshot(os.path.join(base_dir, 'main.jpg'))
        image_name = os.path.join(base_dir, '0.jpg')
        self.xpaths(image_xpaths).screenshot().save(image_name)

        self.swipe_left()  # 尝试滑动

        image_size = 1
        image_elm = self.xpath('//*[@resource-id="com.instagram.android:id/carousel_index_indicator_text_view"]')
        if image_elm.exists:
            try:
                image_size = int(image_elm.text.split('/')[-1])
            except:
                pass

        logging.info('image_size: {}'.format(image_size))

        for index in range(1, image_size):
            logging.info(f"img index: {index}")
            image_elm = self.xpaths(image_xpaths)
            if not image_elm:
                continue
            image_name = os.path.join(base_dir, '{}.jpg'.format(index))
            image_elm.screenshot().save(image_name)
            self.app.screenshot()
            if index != image_size - 1:
                self.swipe_left()

        data = {
            'id': product_id,
            'like_num': like_num,
            'comment_num': comment_num,
            'profile_name': profile_name,
        }
        self.save_result(base_dir, data)
        return True
