# uiautomator_spider

Some crawlers are based on uiautomator2...

### 支持

- [x] dy
- [x] wph
- [x] du
- [x] ins
- [x] tb
- [x] xhs

### run

```
➜  uiautomator_spider git:(main) ✗ python3 spider_main.py -n xhs -k 项链
INFO:root:Can't find any android device. exit
2022-05-03 12:49:05,471 - INFO - Can't find any android device. exit
```

- 需要 usb 连接 android 物理设备

```
➜  uiautomator_spider git:(main) ✗ adb devices 
List of devices attached
```

```shell
➜  uiautomator_spider git:(main) ✗ adb devices                          
List of devices attached
13d4cfdf	device
```

- 再次运行

部分日志：

```
INFO:root:start process new item.....
2022-05-03 01:55:21,057 - INFO - start process new item.....
INFO:root:result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/57dd87ec6f6fbbed72e3a8e346d61871
2022-05-03 01:55:22,818 - INFO - result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/57dd87ec6f6fbbed72e3a8e346d61871
INFO:root:🎉🎉🎉 。。。

2022-05-03 01:55:48,407 - INFO - 🎉🎉🎉 。。。

INFO:root:start process new item.....
2022-05-03 01:55:55,192 - INFO - start process new item.....
INFO:root:result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/51721b66a91d0d90a54f06b48333b8f0
2022-05-03 01:55:57,004 - INFO - result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/51721b66a91d0d90a54f06b48333b8f0
INFO:root:🎉🎉🎉 。。。

2022-05-03 01:56:15,255 - INFO - 🎉🎉🎉 。。。

INFO:root:start process new item.....
2022-05-03 01:56:22,011 - INFO - start process new item.....
INFO:root:result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/4802a1333d633fb7313d84ead344110e
2022-05-03 01:56:23,690 - INFO - result: /Users/beer/uiautomator_spider/xhs/穿戴甲/最新/4802a1333d633fb7313d84ead344110e
INFO:root:🎉🎉🎉 。。。

2022-05-03 01:56:55,065 - INFO - 🎉🎉🎉 。。。
```

- 结果

保存在 **$home_dir/uiautomator_spider** 目录

例子：

```shell
➜  1867497d0112ad4263710253d2ce50b0 pwd
/Users/beer/uiautomator_spider/xhs/穿戴甲/最新/1867497d0112ad4263710253d2ce50b0
➜  1867497d0112ad4263710253d2ce50b0 ll
total 2720
-rw-r--r--  1 beer  staff    98K May  3 01:50 main.png
-rw-r--r--  1 beer  staff   360B May  3 01:49 result.json
-rw-r--r--  1 beer  staff   792K May  3 01:49 1.png
-rw-r--r--  1 beer  staff   456K May  3 01:49 0.png
➜  1867497d0112ad4263710253d2ce50b0 open .
➜  1867497d0112ad4263710253d2ce50b0 cat result.json | jq .
{
  "nickname": "拾壹贰啊",
  "title": "莫名其妙入了穿戴甲的坑",
  "content": "去年一年没有停歇的做美甲，结果指甲像纸片一样薄，今年想试试穿戴甲，真的好绝啊！！！不说根本看不出来是贴的#穿戴甲 ",
  "last_update": "今天 01:38",
  "comment_count": "评论",
  "like_count": "1",
  "collect_count": "收藏"
}
```

![img.png](images/img.png)