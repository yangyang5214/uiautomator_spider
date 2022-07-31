import os
import time

import requests


def save_html(content: str, word: str):
    with open(f'result/{word}.html', 'w') as f:
        f.write(content)


def main():
    with open('1.txt', 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        print(line)

        if os.path.exists(f'result/{line}.html'):
            print('skip...')
            continue
        resp = requests.get('http://127.0.0.1:8081/?url=https://hanyu.baidu.com/zici/s?wd={}'.format(line))
        print(resp.request.url)
        if resp.status_code != 200:
            exit()
        time.sleep(3)
        save_html(resp.text, line)


if __name__ == '__main__':
    main()
