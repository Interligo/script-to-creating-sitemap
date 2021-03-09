from prettytable import PrettyTable

from site_parser import NetworkCrawler
from parser_settings import LINKS


class MainManager:
    """
================================================================
Класс предназначен для создания карты любого сайта.
================================================================
    """
    def __init__(self):
        self.links_to_parse = LINKS
        self.table_heading = [
            'URL сайта',
            'Время обработки',
            'Кол-во найденных ссылок',
            'Имя файла с результатом'
        ]
        self.columns = len(self.table_heading)
        self.table_data = []

    def __str__(self):
        return f'Переданы ссылки для анализа: {self.links_to_parse}'

    def __repr__(self):
        return f'Переданы ссылки для анализа: {self.links_to_parse}'

    def _collect_data_for_table(self, data_to_show):
        self.table_data.extend(data_to_show)

    def _show_results_table(self):
        table = PrettyTable(self.table_heading)

        while self.table_data:
            table.add_row(self.table_data[:self.columns])
            self.table_data = self.table_data[self.columns:]

        print(table)

    def parse_all_links(self):
        for link in self.links_to_parse:
            crawler = NetworkCrawler(link)
            data_to_show = crawler.parse()
            self._collect_data_for_table(data_to_show)

        self._show_results_table()
