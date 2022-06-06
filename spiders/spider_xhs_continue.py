import json
import os

import uiautomator2 as u2

input_file = 'continue.csv'

target_dir = 'continue'

os.makedirs(target_dir, exist_ok=True)

like_xpath = '//*[@resource-id="com.xingin.xhs:id/dzk"]'
collect_xpath = '//*[@resource-id="com.xingin.xhs:id/dyg"]'
comment_xpath = '//*[@resource-id="com.xingin.xhs:id/dym"]'
page_list_xpath = '//*[@resource-id="com.xingin.xhs:id/dcy"]/android.widget.FrameLayout//android.view.View'
search_input_xpath = '//*[@resource-id="com.xingin.xhs:id/f20"]'
search_text_xpath = '//*[@resource-id="com.xingin.xhs:id/ddd"]'
search_click = '//*[@resource-id="com.xingin.xhs:id/ddh"]'


def get_search_keyword():
    if not os.path.exists(input_file):
        print("请把文件放在当前目录, 并命名为 continue.csv")
        exit(-1)
    with open(input_file, 'r') as f:
        for line in f.readlines():
            arr = line.split(",")
            yield arr[0], arr[1], arr[2]


package_name = 'com.xingin.xhs'


def get_all_text(app, xpath=None):
    if not xpath:
        xpath = '//android.widget.TextView'
    return [_.text.strip() for _ in app.xpath(xpath).all() if _.text.strip()]


def flag(result_path):
    with open(result_path, 'w') as f:
        json.dump({}, f, ensure_ascii=False)


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

        app.sleep(10)

        print("process: {} {}".format(keyword, auther))

        app.xpath(search_text_xpath).set_text(keyword)
        app.sleep(2)
        app.xpath(search_click).click()
        app.sleep(3)

        all_items = app.xpath(page_list_xpath).all()

        data = {}
        for item in all_items:
            print('new item...')

            item.click()  # 跳转

            app.sleep(5)

            nickname = app.xpath('//*[@resource-id="com.xingin.xhs:id/nickNameTV"]')
            if not nickname.exists:  # 非详情页面
                if len(app.xpath(page_list_xpath).all()) != len(all_items):  # 跳转了
                    app.keyevent('4')  # 返回列表页
                continue

            if nickname.text != auther:
                app.keyevent('4')
                app.sleep(3)
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

            app.keyevent('4')  # 返回到列表页
            app.sleep(5)
            break

        with open(result_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)

        app.keyevent('4')  # 返回到搜索页
        app.sleep(3)

        print("-" * 10)


if __name__ == '__main__':
    main()
