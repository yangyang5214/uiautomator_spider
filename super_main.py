# -*- coding: UTF-8 -*-
import sys
import os


def main(base_dir: str, task_txt_file: str):
    final_path = os.path.join(base_dir, task_txt_file)
    if not os.path.exists(final_path):
        print('final_path: {}, not exists'.format(final_path))
        return
    print('use task file: {}'.format(final_path))
    with open(final_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        print('*' * 30)
        line = f"cd {base_dir} && " + line
        print(line)
        print('*' * 30)
        os.system(line)


if __name__ == '__main__':
    base_dir = os.path.dirname(sys.argv[0])
    try:
        task_txt_file = sys.argv[1]
    except:
        task_txt_file = 'task.txt'
    main(base_dir, task_txt_file)
