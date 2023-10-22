import uiautomator2 as u2


def main():
    app = u2.connect()
    elm = app.xpath('//*[@resource-id="com.xingin.xhs:id/noteContentText"]').get_text()
    print(elm)


if __name__ == '__main__':
    main()
