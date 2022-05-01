# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, log


class SpiderTb(SpiderBase):
    name = "tb"
    package_name = 'com.taobao.taobao'

    def __init__(self, keyword):
        super().__init__(keyword)

    def _process_keyword(self, start_price, end_price):
        log.info("click 【搜索栏】")
        self.app.xpath('//*[@content-desc="搜索栏"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]').click()
        log.info("set 【{}】关键词".format(self.keyword))
        self.app.xpath('//*[@resource-id="com.taobao.taobao:id/searchEdit"]').set_text(self.keyword)

        self.sleep_random()

        self.app.press('enter')
        self.app.implicitly_wait(10 * 3)

        try:
            log.info("click【销量】btn")
            self.app.xpath('//*[@text="销量"]').click()
        except:
            self._error("销量 排序点击失效{}".format(self.screen_debug()))

        self.sleep(10)

        log.info("set price {} {}".format(start_price, end_price))
        self.app.xpath('//*[@resource-id="com.taobao.taobao:id/filterBtn"]').click()

        try:
            self.app.xpath('//*[@text="自定最低价"]').set_text(str(start_price))
            self.app.xpath('//*[@text="自定最高价"]').set_text(str(end_price))
        except:
            pass

        self.sleep(1)

        self.app.xpath('//*[@content-desc="关闭筛选"]').click()

        i = 0
        while i < 20:
            self.sleep(3)
            temp_lists = self.app.xpath('//*[@resource-id="com.taobao.taobao:id/libsf_srp_header_list_recycler"]/android.widget.FrameLayout').all()
            for item in temp_lists:
                item.click()
                self.app.implicitly_wait(20)
                flag = self.process_item("{}_{}".format(start_price, end_price))
                if flag:
                    self.return_pre()
            i += 1
            self.swipe_down()
            self.app.implicitly_wait(10)

    def process_item(self, price_str: str):
        log.info('start process new item.....')
        self.sleep_random()
        all_text = self.app.xpath('//android.widget.TextView').all()
        all_texts = [_.text.strip() for _ in all_text]
        sales = None
        prices = []
        price_flag = False
        image_size = 0

        max_length = -1
        product_name = None
        for text in all_texts:
            if len(text) > max_length:
                max_length = len(text)
                product_name = text  # 取最长的作为 product_name

            # 都是 1/6 1/5 之类的
            if "/" in text and len(text) == 3 and image_size == 0:
                image_size = int(text.split('/')[-1])

            if text == '￥':
                price_flag = True
            elif price_flag:
                prices.append(text)
                price_flag = False
            elif text.startswith('月销'):
                sales = text

        if not prices:
            return False

        product_id = None
        if product_name:
            product_id = self.get_product_id(product_name)
        else:
            self._error("Cannot get product_name, {}".format(self.screen_debug()))

        base_dir = self.base_dir(price_str, product_id)
        if os.path.exists(self.get_result_path(base_dir)):
            log.info("cache... skip\n")
            return True

        log.info('开始处理图片。。。image_size: {}'.format(image_size))

        image_name = os.path.join(base_dir, 'main.png')
        self.app.screenshot(image_name)

        for index in range(1, image_size):
            log.info("current index {}".format(index))
            self.app.swipe(400, 300, 100, 300, 0.1)
            img_elm = self.xpath('//*[@resource-id="com.taobao.taobao:id/mainpage2"]/android.widget.RelativeLayout[1]')
            image_name = os.path.join(base_dir, '{}.png'.format(index))
            if img_elm.exists:
                img_elm.screenshot().save(image_name)
            self.sleep_random()

        data = {
            'product_id': product_id,
            'price': prices[0],
            'second_price': prices[1] if len(prices) > 1 else prices[0],
            'product_name': product_name,
            'sales': sales,
        }
        self.save_result(base_dir, data)
        return True
