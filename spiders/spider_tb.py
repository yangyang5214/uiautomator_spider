# -*- coding: UTF-8 -*-
from spiders.spider_base import SpiderBase


class SpiderTb(SpiderBase):
    name = "tb"
    package_name = 'com.taobao.taobao'

    def __init__(self, keyword):
        super().__init__(keyword)
