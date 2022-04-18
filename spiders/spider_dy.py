# -*- coding: UTF-8 -*-
from spiders.spider_base import SpiderBase

"""
dou_yin spider
"""


class SpiderDy(SpiderBase):
    name = "dy"
    package_name = 'com.taobao.taobao'

    def __init__(self, keyword):
        super().__init__(keyword)
