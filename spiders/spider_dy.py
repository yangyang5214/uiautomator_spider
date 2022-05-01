# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, log

"""
dou_yin spider
"""


class SpiderDy(SpiderBase):
    name = "dy"
    package_name = 'com.ss.android.ugc.aweme'
    activity = '.main.MainActivity'
    page_limit = 30
    prices = [0, 0]
    search_keyword_xpath = '//*[@resource-id="com.ss.android.ugc.aweme:id/fqb"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.text.UIText'
    search_keyword_confirm_xpath = '//*[@resource-id="com.ss.android.ugc.aweme:id/p3l"]'
    page_list_xpath = '//*[@resource-id="com.ss.android.ugc.aweme:id/h1y"]/android.view.ViewGroup//android.widget.ImageView'

    product_choose_xpath = None
    start_price_xpath = None
    end_price_xpath = None
    product_choose_confirm_xpath = None
    sale_xpath = '//*[@text="销量"]'

    watchers = [
        '//*[@resource-id="com.ss.android.ugc.aweme:id/tv_cancel"]',
        '//*[@resource-id="com.ss.android.ugc.aweme:id/c9k"]'
    ]

    def __init__(self, keyword):
        super().__init__(keyword)

    def _process_keyword(self, start_price, end_price):
        log.info('click 【我】 btn...')
        self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/root_view"]/android.widget.FrameLayout[5]').click()

        log.info('click 【抖音商城】 btn...')
        self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/j67"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').click()

        self.do_search_keyword()

        self.click_sale(self.sale_xpath)

        self.process_page_list(start_price, end_price)

    def pass_item(self, item):
        """
        跳过小图片，可能不是 商品的主图
        :param item:
        :return:
        """
        # width or height < 300 , skip
        if item.rect[2] < 300 or item.rect[3] < 300:
            return True
        return False

    def _process_item(self, price_str: str):
        product_name_elm = self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/6y"]')
        if not product_name_elm.exists:
            log.info("可能是 视频链接 。。。skip")
            return
        product_name = product_name_elm.text
        product_id = self.get_product_id(product_name)

        base_dir = self.base_dir(price_str, product_id)
        result_path = SpiderBase.get_result_path(base_dir)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        elif os.path.exists(result_path):
            log.info('hit cache ... skip')
            return

        all_texts = self.get_all_text()
        prices = []
        sales = None
        for text in all_texts:
            if '已售' in text:
                sales = text
            elif text.startswith("¥"):
                prices.append(text)
        if not sales:
            sales_xpath = [
                '//*[@resource-id="com.ss.android.ugc.aweme:id/l_g"]',
                '//*[@resource-id="com.ss.android.ugc.aweme:id/za"]'
            ]
            for x in sales_xpath:
                elm = self.xpath(x)
                if elm.exists:
                    sales = elm.text
                    break

        self.app.screenshot(os.path.join(base_dir, 'main.png'))

        # 点击图片，到大图
        self.app.click(300, 300)
        self.sleep(2)

        image_name = os.path.join(base_dir, '0.png')
        self.app.screenshot(image_name)

        image_size = SpiderBase.get_image_size(self.get_all_text())

        for i in range(1, image_size - 1):
            self.app.swipe(700, 300, 100, 300, 0.1)
            log.info("swipe...{}".format(i))
            self.sleep(3)
            image_name = os.path.join(base_dir, str(i) + '.png')
            self.app.screenshot(image_name)
        self.return_pre()

        # 获取 评价数量
        for i in range(10):  # 最大尝试 10 次
            if not self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/28"]').exists:
                self.app.swipe(300, 600, 300, 500, 0.035)
            else:
                break
        try:
            comment = {
                'count': self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/29"]').text,
                'tags': [item.text for item in self.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/28"]/android.widget.FrameLayout//android.widget.TextView').all()]
            }
        except:
            comment = None
        data = {
            'product_id': product_id,
            'price': prices[0],
            'original_price': prices[1] if len(prices) > 1 else prices[0],
            'product_name': product_name,
            'sales': sales,
            'comment': comment
        }
        self.save_result(base_dir, data)
