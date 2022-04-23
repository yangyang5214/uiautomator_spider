# -*- coding: UTF-8 -*-


import uiautomator2 as u2

if __name__ == '__main__':
    import os
    os.system("afplay /Users/beer/vlog/mp3s/hai_bian.mp3")
    exit()

    app = u2.connect()
    app.app_start('com.ss.android.ugc.aweme', stop=False, activity='.main.MainActivity')
    tags =  [item.text for item in app.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/28"]/android.widget.FrameLayout//android.widget.TextView').all()]
    all_text = [_.text.strip() for _ in app.xpath('//android.widget.TextView').all()]

    for _ in all_text:
        print(_)
        print("-----")
        print(len(_))
