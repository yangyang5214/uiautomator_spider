from datetime import datetime
import os
import subprocess

user_root_home = os.path.expanduser('~')

base_dir = os.path.join(user_root_home, "uiautomator_spider")

import shutil
import requests

server_ip = ''

today_str = datetime.today().strftime('%Y%m%d')


def main():
    print(f': {base_dir}')
    os.chdir(base_dir)

    find_cmd = f"find {base_dir} -name '*json' -mtime -100"
    print(f"cmd: {find_cmd}")
    out, _ = subprocess.Popen(find_cmd, stdout=subprocess.PIPE, shell=True).communicate()
    try:
        out = out.decode('utf-8').strip()
    except:
        out = out.decode('gbk').strip()
    all_files = out.split("\n")
    if not all_files:
        print("no file found, exit!")
        return

    print(f'all_files: {all_files}')

    for file_path in all_files:
        file_path = file_path.strip('"')
        dir_name = os.path.dirname(file_path)
        if not dir_name:
            continue
        target_dir = dir_name.replace('uiautomator_spider', today_str)
        target_dir = os.path.dirname(target_dir)
        print(f'target_dir: {target_dir}')
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        else:
            os.makedirs(target_dir)
        print(f"move {dir_name} to {target_dir}")
        shutil.move(dir_name, target_dir)

    os.chdir(os.path.join(os.path.expanduser('~')))
    shutil.make_archive(today_str, 'zip', root_dir=today_str)


def upload(filepath: str):
    if not os.path.exists(filepath):
        return
    print('start upload file .....')
    try:
        resp = requests.post(f'http://{server_ip}:9991/spider/upload', auth=('up_agent', 'hdd_20220804~'), files={
            'file': open(filepath, 'rb'),
        })
        if resp.status_code == 200:
            print('upload success')
        else:
            print(resp.text)
    except Exception as e:
        print(f'upload error. {e}')


if __name__ == '__main__':
    main()
    exit()
    upload(os.path.join(user_root_home, today_str + ".zip"))
