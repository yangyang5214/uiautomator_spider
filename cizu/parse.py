import os

from bs4 import BeautifulSoup
from lxml import etree
import csv


def main():
    with open('result.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["字词", "释义", "近义词", "反义词"])

        for file in os.listdir('result'):
            with open(f'result/{file}', 'r') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                html = etree.HTML(str(soup))
                cizu = file.replace('.html', '')
                means = html.xpath("//div[@class='content means imeans']//dd/p//text()")
                if not means:
                    means = ['']

                synonym = []
                antonym = []

                try:
                    synonym = html.xpath("//div[@id='synonym']//a//text()")
                    antonym = html.xpath("//div[@id='antonym']//a//text()")
                except:
                    pass
                csv_writer.writerow([cizu, " ".join(synonym), " ".join(antonym), means[0].replace(' ', '').replace('\n', '')])


if __name__ == '__main__':
    main()
