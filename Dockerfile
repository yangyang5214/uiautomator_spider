FROM cdrx/pyinstaller-windows

RUN mkdir uiautomator_spider

COPY . /src/uiautomator_spider

WORKDIR /src/uiautomator_spider

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

ENTRYPOINT ["/bin/bash", "cd uiautomator_spider && pyinstaller -w -F spider_main.py -n uiautomator_spider.exe"]

