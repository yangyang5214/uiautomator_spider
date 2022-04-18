# -*- coding: UTF-8 -*-


import uiautomator2 as u2

if __name__ == '__main__':
    app = u2.connect()
    all_text = [_.text.strip() for _ in app.xpath('//android.widget.TextView').all()]

    for _ in all_text:
        print(_)
        print("-----")
        print(len(_))
