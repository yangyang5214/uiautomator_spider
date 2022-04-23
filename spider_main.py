# -*- coding: UTF-8 -*-
import argparse

from spiders.spider_base import SpiderBase


def main(spider: SpiderBase):
    spider.process()


if __name__ == '__main__':
    spider_map = {}
    for sub in SpiderBase.__subclasses__():
        spider_map[sub.name] = sub

    parser = argparse.ArgumentParser(description='Collect some data by spider...')
    parser.add_argument('-n', '--name', help='spider name...', choices=spider_map.keys())
    parser.add_argument('-k', '--keyword', help='spider keyword... eg: 项链', required=False)
    args = parser.parse_args()

    main(spider_map.get(args.name, SpiderBase)(args.keyword))
