# -*- coding: UTF-8 -*-

import os

from spiders.spider_base import SpiderBase, logging

"""
dou_yin spider
"""


class SpiderDingDong(SpiderBase):
    name = "dd"
    package_name = 'com.yaya.zone'

    stop = False

    def __init__(self, keyword):
        super().__init__(keyword)

    def process(self):
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
        # play mac local mp3 file
        os.system("afplay /Users/beer/vlog/mp3s/hai_bian.mp3")

    def has_rider(self):
        tv_one_elm = self.xpath('//*[@resource-id="com.yaya.zone:id/tv_one"]')
        if tv_one_elm.exists and tv_one_elm.text == '由于近期疫情问题，配送运力紧张，本站点当前运力已约满':
            return False
        return True
