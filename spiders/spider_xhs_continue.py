import json
import os

import uiautomator2 as u2

from spider_xhs import *

input_file = 'continue.csv'

target_dir = 'continue'

os.makedirs(target_dir, exist_ok=True)


def get_search_keyword():
    with open(input_file, 'r') as f:
        for line in f.readlines():
            arr = line.split(",")
            yield arr[0], arr[1], arr[2]


package_name = 'com.xingin.xhs'


def get_all_text(app, xpath=None):
    if not xpath:
        xpath = '//android.widget.TextView'
    return [_.text.strip() for _ in app.xpath(xpath).all() if _.text.strip()]


def swipe_right(app):
    """
    右滑
    :return:
    """
    app.sleep(1.5)
    app.swipe(0, 600, 300, 600, 0.1)
    app.sleep(1.5)


def main():
    app = u2.connect()
    app.app_start(package_name, stop=True)
    app.sleep(10)

    app.xpath(search_input_xpath).click()

    for _id, keyword, auther in get_search_keyword():
        result_path = os.path.join(target_dir, _id + ".json")
        if os.path.exists(result_path):
            print('cached, skip')
            continue

        print(keyword, auther)

        app.xpath(search_text_xpath).set_text(keyword)
        app.xpath(search_click).click()
        app.sleep(3)

        if auther not in get_all_text(app):
            swipe_right(app)
            continue  # 不存在

        all_items = app.xpath(page_list_xpath).all()
        for item in all_items:
            item.click()

            try:
                item.click()
            except:
                pass  # 二次点击，确保跳转
            app.sleep(3)

            app.click(300, 300)

            nickname = app.xpath('//*[@resource-id="com.xingin.xhs:id/nickNameTV"]')
            if not nickname.exists or nickname.text != auther:
                swipe_right(app)
                continue
            like_count = app.xpath(like_xpath).text
            collect_count = app.xpath(collect_xpath).text
            comment_count = app.xpath(comment_xpath).text

            data = {
                'comment_count': comment_count,
                'like_count': like_count,
                'collect_count': collect_count,
                "title": keyword,
                "auth": auther,
                "id": _id
            }

            with open(result_path, 'w') as f:
                json.dump(data, f, ensure_ascii=False)

            app.sleep(8)

            swipe_right(app)
            break
        swipe_right(app)


if __name__ == '__main__':
    main()
