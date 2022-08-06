> 自动上传

### auto_upload_main.py

此脚本，会收集当前日期创建的文件结果，并压缩为 **20220806.zip** 的格式

配置 计划任务 可以配置为每天的快结束时间段 比如: 23:00 之类的

### spider_agent

此文件是服务端接受 👆 上传的文件夹。

需要 配置 **config.toml** 文件，修改指定的上传路径， 例子： **target_dir = '/tmp'**

```shell
./spider_agent 简单启动
```


- systemctl 托管

```shell

```