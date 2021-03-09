from sqlalchemy import Column
from sqlalchemy import JSON
from sqlalchemy import Integer
from sqlalchemy import TEXT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseModel(Base):
    """Базовая модель для базы данных."""
    __abstract__ = True
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    def __str__(self):
        return f'Экземпляр класса {__class__.__name__}'

    def __repr__(self):
        return __class__.__name__


class SiteMap(BaseModel):
    """Модель карты сайта для создания таблицы в базе данных."""
    __tablename__ = 'sitemap'
    main_url = Column(TEXT, nullable=False)
    found_url = Column(JSON, nullable=False)
    links_count = Column(Integer, nullable=False)
    processing_time = Column(Integer, nullable=False)

    def __init__(self, main_url, found_url, links_count, processing_time):
        self.main_url = main_url
        self.found_url = found_url
        self.links_count = links_count
        self.processing_time = processing_time

    def __str__(self):
        return f'main_url: {self.main_url}, found_url: {self.found_url}'

    def __repr__(self):
        return f'main_url: {self.main_url}'

    def __getitem__(self, key):
        return getattr(self, key)
