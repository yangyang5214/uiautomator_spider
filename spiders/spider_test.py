# -*- coding: UTF-8 -*-


import uiautomator2 as u2


def get_all_text(app, xpath=None):
    if not xpath:
        xpath = '//android.widget.TextView'
    return [_.text.strip() for _ in app.xpath(xpath).all() if _.text.strip()]


if __name__ == '__main__':
    app = u2.connect()

    image_elm = app.xpath('//*[@resource-id="com.shizhuang.duapp:id/flImageViewpager"]')
    image_elm.screenshot().save('1.jpg')
    image_elm.screenshot().save('1.jpg')
