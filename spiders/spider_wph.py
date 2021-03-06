# -*- coding: UTF-8 -*-
import os

from spiders.spider_base import SpiderBase, log as logging

"""
wph spider
"""


class SpiderWph(SpiderBase):
    name = "wph"
    package_name = 'com.achievo.vipshop'

    item_limit = 80
    prices = [100, 200]

    search_keyword_xpath = '//*[@resource-id="com.achievo.vipshop:id/search_text_view"]'
    search_keyword_confirm_xpath = '//*[@resource-id="com.achievo.vipshop:id/search_btn"]'
    sale_xpath = '//*[@resource-id="com.achievo.vipshop:id/text_sales_volume"]'

    product_choose_xpath = '//*[@resource-id="com.achievo.vipshop:id/text_products_choose"]'
    start_price_xpath = '//*[@resource-id="com.achievo.vipshop:id/min_price_range"]'
    end_price_xpath = '//*[@resource-id="com.achievo.vipshop:id/max_price_range"]'
    product_choose_confirm_xpath = '//*[@resource-id="com.achievo.vipshop:id/btn_confirm"]'
    page_list_xpath = '//*[@resource-id="com.achievo.vipshop:id/product_list_content_container"]//android.widget.RelativeLayout//android.widget.ImageView'

    watchers = [
        '//*[@resource-id="com.achievo.vipshop:id/ll_button"]',  # 我知道了按钮
        '//*[@resource-id="com.achievo.vipshop:id/left_button"]'  # 软件更新
    ]

    def _process_keyword(self, start_price, end_price):
        # 点击输入框，跳转到主 输入页面
        self.xpath('//*[@resource-id="com.achievo.vipshop:id/index_search_hint"]').click()
        self.sleep_random()

        self.do_search_keyword()
        self.sleep_random()

        self.click_sale(self.sale_xpath)
        self.sleep_random()

        self.range_price(start_price, end_price)
        self.sleep_random()

        self.process_page_list(start_price, end_price)
        self.sleep_random()

    def pass_item(self, item):
        """
        跳过小图片，可能不是 商品的主图
        :param item:
        :return:
        """
        if item.rect[2] != 275:
            return True
        return False

    def _process_item(self, price_str: str):
        all_texts = self.get_all_text()
        sales = None
        prices = []
        image_size = 0
        max_length = -1
        product_name = None
        for text in all_texts:
            # 一次 分期 的信息 比较长
            if '分期' not in text and len(text) > max_length:
                max_length = len(text)
                product_name = text  # 取最长的作为 product_name

            # 都是 1/6 1/5 之类的
            if not image_size and "/" in text and len(text) <= 4:  # 1/9 1/11 限制长度
                image_size = int(text.split('/')[1])
            elif text.startswith('¥'):
                prices.append(text)
            elif '付款' in text and '想要' in text:
                sales = text

        product_id = None
        if product_name:
            product_id = self.get_product_id(product_name)
        else:
            exit(-1)

        base_dir = self.base_dir(price_str, product_id)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        if product_name and image_size == 0:
            # 可能是页面最下面点到了购物车
            os.system("rm -rf {}".format(base_dir))
            logging.info('🎉🎉🎉 。。。skip 购物车 \n')
            return

        self.app.screenshot(os.path.join(base_dir, 'main.jpg'))

        logging.info('开始处理图片。。。image_size: {}'.format(image_size))

        for i in range(image_size - 1):
            self.swipe_left()
            logging.info("image index: {}".format(i))
            image_name = os.path.join(base_dir, str(i) + '.jpg')
            if os.path.exists(image_name):
                logging.info("image cached, skip")
                continue
            elm = self.xpath('//*[@resource-id="com.achievo.vipshop:id/product_gallery_layout"]')
            if elm.exists:
                elm.screenshot().save(image_name)
                self.sleep_random()
            else:
                exit(-1)

        # 获取 评价数量
        for i in range(10):  # 最大尝试 10 次
            if not self.xpath('//*[@resource-id="com.achievo.vipshop:id/size_feel_xf"]//android.widget.TextView').exists:
                self.app.swipe(300, 600, 300, 500, 0.035)
            else:
                break
        try:
            comment = {
                'count': self.xpath('//*[@resource-id="com.achievo.vipshop:id/tv_comment_title"]').text,
                'percentage': self.xpath('//*[@resource-id="com.achievo.vipshop:id/tag_titles"]').text,
                'tags': [item.text for item in self.xpath('//*[@resource-id="com.achievo.vipshop:id/size_feel_xf"]//android.widget.TextView').all()]
            }
        except:
            comment = None
        data = {
            'product_id': product_id,
            'price': prices[0],
            'original_price': prices[1] if len(prices) > 1 else prices[0],
            'product_name': product_name,
            'sales': sales,
            'comment': comment,
        }
        self.save_result(base_dir, data)
