# -*- coding: UTF-8 -*-

import os

from spiders.spider_base import SpiderBase, log as logging

"""
dou_yin spider
"""


class SpiderDingDong(SpiderBase):
    name = "dd"
    package_name = 'com.yaya.zone'

    stop = True

    def __init__(self, keyword):
        super().__init__(keyword)

    def process_yun_li(self):
        """
        监控 运力
        :return:
        """
        while True:
            logging.info("try 🚄 ... ")
            self.xpath('//*[@resource-id="com.yaya.zone:id/ani_home"]').click()
            self.sleep_random(1, 3)
            if self.has_rider():
                break
        self.alarm()

    def has_rider(self):
        tv_one_elm = self.xpath('//*[@resource-id="com.yaya.zone:id/tv_one"]')
        if tv_one_elm.exists and tv_one_elm.text == '由于近期疫情问题，配送运力紧张，本站点当前运力已约满':
            return False
        return True

    def alarm(self):
        # play mac local mp3 file
        os.system("afplay /Users/beer/vlog/mp3s/hai_bian.mp3")

    def process(self):
        flag = True
        while flag:
            logging.info("retry ................ 🚄")
            # 购物车
            self.xpath('//*[@resource-id="com.yaya.zone:id/rl_car_layout"]').click()
            # 去结算
            self.xpath('//*[@resource-id="com.yaya.zone:id/btn_submit"]').click()
            # 去支付
            self.xpath('//*[@resource-id="com.yaya.zone:id/tv_submit"]').click()
            all_rv_selected_hour_elm = self.xpath('//*[@resource-id="com.yaya.zone:id/rv_selected_hour"]/android.view.ViewGroup/android.widget.TextView')
            while not all_rv_selected_hour_elm.exists:
                # 去支付
                self.xpath('//*[@resource-id="com.yaya.zone:id/tv_submit"]').click()
                all_rv_selected_hour_elm = self.xpath('//*[@resource-id="com.yaya.zone:id/rv_selected_hour"]/android.view.ViewGroup/android.widget.TextView')

            all_rv_selected_hour = all_rv_selected_hour_elm.all()
            for index in range(1, len(all_rv_selected_hour), 2):
                item = all_rv_selected_hour[index]
                logging.info("text: {}".format(item.text))
                if '已约满' not in item.text:
                    try:
                        item.click()
                        self.xpath('//*[@resource-id="com.yaya.zone:id/tv_submit"]').click()
                    except:
                        pass
                    flag = False
                    break
            if flag:
                self.return_pre(2)
        self.alarm()
