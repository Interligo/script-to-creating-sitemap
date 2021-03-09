import os

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from db_models import SiteMap


class DataBaseManager:
    """
=============================================================
Класс предназначен для взаимодействия с базой данных SQLite3.
=============================================================
    """

    def __init__(self, domain_name):
        self.meta = MetaData()
        self.db_name = domain_name
        self.data_storage = 'service_files'
        if not os.path.exists(self.data_storage):
            os.makedirs(self.data_storage)
        self._prepare_to_save_new_map()
        self._create_table()

    def __str__(self):
        return f'База данных для сайта {self.db_name}'

    def __repr__(self):
        return f'БД {self.db_name}'

    def _get_connection(self):
        """Возвращает подключение к SQLite3."""
        engine = create_engine(f'sqlite:///{self.data_storage}//{self.db_name}_site_map.db', pool_pre_ping=True)
        return engine

    def _create_session(self):
        """Создает сессию для взаимодействия с базой данных."""
        engine = self._get_connection()
        db_session = sessionmaker(engine)
        session = db_session()
        return session

    def _create_table(self):
        """Создает таблицу из модели."""
        engine = self._get_connection()
        SiteMap.metadata.create_all(engine)

    def _prepare_to_save_new_map(self):
        """Удаляет таблицу с устаревшими данными перед сохранением новой карты сайта."""
        engine = self._get_connection()
        try:
            SiteMap.__table__.drop(engine)
        except OperationalError:
            pass

    def save_data_to_db(self, main_url, found_url, links_count, processing_time):
        """Сохраняет данные в БД."""
        session = self._create_session()
        new_data = SiteMap(
            main_url=main_url,
            found_url=found_url,
            links_count=links_count,
            processing_time=processing_time
        )
        session.add(new_data)
        try:
            session.commit()
        except OperationalError as error:
            return f'Возникла ошибка: {error}.'

    def get_all_data_from_db(self):
        """Выгружает все данные из БД."""
        session = self._create_session()
        all_data = session.query(SiteMap).all()
        return all_data

    def get_time_from_db(self):
        """Выгружает время работы из БД."""
        session = self._create_session()
        all_processing_time = session.query(SiteMap.processing_time).all()
        return all_processing_time

    def get_total_time_from_db(self):
        """Высчитывает общее время работы."""
        processing_time = self.get_time_from_db()
        total_time = round(sum([float(working_time) for (working_time,) in processing_time]), 3)
        return total_time

    def get_links_count_from_db(self):
        """Выгружает количество ссылок из БД."""
        session = self._create_session()
        all_links_count = session.query(SiteMap.links_count).all()
        return all_links_count

    def get_total_links_count_from_db(self):
        """Высчитывает общее количество найденных ссылок."""
        all_links = self.get_links_count_from_db()
        links_count = sum([int(link) for (link,) in all_links])
        return links_count
