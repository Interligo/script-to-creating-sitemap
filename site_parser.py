import os
import time
import json
import random

import requests
import xml.etree.ElementTree as et
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs
from requests.exceptions import InvalidURL, ConnectionError

from db_management import DataBaseManager


class NetworkCrawler:
    """
===================================================
Класс предназначен для создания карты любого сайта.
===================================================
    """
    def __init__(self, link: str):
        self.session = requests.Session()
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.190 Safari/537.36'
        }
        self.main_link = link
        self.domain_name = urlparse(self.main_link).hostname
        self.db = DataBaseManager(self.domain_name)
        self.links_to_check = [link]
        self.checked_links = []
        self.current_link = None
        self.current_links_list = []
        self.result_dir = 'script_results'
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        self.result_file = self.domain_name + '_sitemap.xml'

    def __str__(self):
        return f'Карта сайта {self.main_link}'

    def __repr__(self):
        return f'{self.main_link}'

    def _make_indent_in_xml(self, elem, level=0):
        """Функция добавляет отступы при записи xml-файла."""
        i = '\n' + level * '  '
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._make_indent_in_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def save_data_to_xml(self):
        """Сохраняет данные из базы данных в xml-файл."""
        root = et.Element('urlset', xmlns="http://www.sitemap.org/shemas/sitemap/0.9")

        all_data = self.db.get_all_data_from_db()
        for element in all_data:
            urls = element['found_url']

            if urls != '[]':
                decoded_urls = json.loads(urls)

                for url in decoded_urls:
                    url_block = et.Element('url')
                    loc_block = et.Element('loc')
                    loc_block.text = url
                    url_block.append(loc_block)
                    root.append(url_block)

        self._make_indent_in_xml(root)
        etree = et.ElementTree(root)
        file_to_write = open(f'{self.result_dir}/{self.result_file}', 'wb')
        etree.write(file_to_write, encoding='UTF-8', xml_declaration=True)

    def parse(self):
        """Анализирует сайт по ссылке и сохраняет спарсенные данные в базы данных."""
        print(f'Приступаю к анализу {self.main_link}.')

        while len(self.links_to_check) != 0:
            it = iter(self.links_to_check)
            link = next(it)

            self.current_link = link
            self.current_links_list.clear()
            self.links_to_check.remove(self.current_link)
            self.checked_links.append(self.current_link)
            work_start_time = time.time()

            if self.domain_name in self.current_link:
                try:
                    response = self.session.get(self.current_link, headers=self.headers)
                    time.sleep(random.randint(2, 4))

                    if response.status_code == 200:
                        soup = bs(response.content, 'lxml')
                        all_a_tags = soup.find_all('a')

                        for url in all_a_tags:
                            url_link = url.get('href')
                            try:
                                if url_link.startswith('http'):
                                    full_link = url_link
                                elif url_link.startswith('?'):
                                    continue
                                else:
                                    full_link = self.main_link + url_link

                                if full_link not in self.links_to_check and full_link not in self.checked_links:
                                    self.current_links_list.append(full_link)
                                    self.links_to_check.append(full_link)
                            except AttributeError:
                                continue

                        processing_time = round((time.time() - work_start_time), 3)
                        links_count = len(self.current_links_list)
                        links_list_json = json.dumps(self.current_links_list)
                        self.db.save_data_to_db(self.current_link, links_list_json, links_count, processing_time)

                    else:
                        print(f'{self.current_link} не отвечает на запросы.')

                except (InvalidURL, ConnectionError):
                    pass

        self.save_data_to_xml()
        print(f'Работа завершена. '
              f'Карта сайта находится в {os.path.join(os.getcwd(), self.result_dir, self.result_file)}')

        data_to_show = []
        data_to_show.append(self.main_link)
        data_to_show.append(self.db.get_total_time_from_db())
        data_to_show.append(self.db.get_total_links_count_from_db())
        data_to_show.append(self.result_file)

        return data_to_show
