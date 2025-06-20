import time
import logging
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, Index, Table, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from constants.constants import DATABASE_NAME, PATH_FOR_BACKUP

_registry = {}
_models = {}


def register_model(cls):
    """Декоратор для автоматической регистрации моделей"""
    _registry[cls.__name__] = cls
    return cls


SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DATABASE_NAME}"


def backup_db_if_exists(db_path):
    if not os.path.exists(db_path):
        return
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    base_name, ext = os.path.splitext(db_path)
    backup_path = f"{base_name}_{yesterday_str}{ext}"

    # Формируем имя для резервной копии (без расширения)
    base_name, ext = os.path.splitext(db_path)
    backup_name = f"{base_name}_{yesterday_str}"
    backup_db_path = f"{backup_name}{ext}"  # Полный путь к копии БД
    backup_zip_path = backup_zip_path = os.path.join(PATH_FOR_BACKUP, f"{backup_name}.zip")

    # Если архив уже существует, ничего не делаем
    if os.path.exists(backup_zip_path):
        # _send_email("[Datelite]", f"Создана временная копия: {backup_db_path}")
        return

    temp_filename = tempfile.mktemp(suffix='.db')
    # Создаём временную копию файла БД
    try:
        try:
            shutil.copy2(db_path, temp_filename)
            # _send_email("[Datelite]", f"Создана временная копия: {temp_filename}")
        except Exception as e:
            # print(f"Ошибка при создании временной копии: {e}")
            return

        # Архивируем файл в ZIP
        try:
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_filename, arcname=backup_db_path)
                # print(f"Создан архив: {backup_zip_path}")
        except Exception as e:
            # print(f"Ошибка при создании архива: {e}")
            # _send_email("[Datelite]", "Ошибка при создании архива:")
            return
    finally:
        # Удаляем временный файл вручную
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


# backup_db_if_exists(DATABASE_NAME)

class Database:
    def __init__(self, echo: bool = False, database_url: str = SQLALCHEMY_DATABASE_URL):
        logging.info("Инициализация Базы данных")
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
        self.engine.echo = echo

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        self.Base = declarative_base()
        self.setup_models()

        self.init_db()

    def init_db(self):
        self.Base.metadata.create_all(bind=self.engine)
        self._ensure_indexes()

    def setup_models(self):
        logging.info("Инициализация моделей")
        for name, model_cls in _registry.items():
            # Создаем класс модели с привязкой к Base
            logging.info(f"Инициализация модели: {name}")
            model = type(name, (self.Base, model_cls), {})
            _models[name] = model

    def get_session(self):
        """Возвращает новый сеанс базы данных"""
        return self.SessionLocal()

    def drop_all(self):
        """Удаляет все таблицы из базы данных"""
        self.Base.metadata.drop_all(bind=self.engine)

    def _ensure_indexes(self):
        inspector = inspect(self.engine)

        # Конфигурация индексов для создания
        INDEX_CONFIGS = [
            {'name': 'mark_id_is_deleted', 'table': 'mark_image', 'columns': ['mark_id', 'is_deleted']},
            {'name': 'id_mark_id_is_deleted', 'table': 'mark_image', 'columns': ['mark_id', 'is_deleted', 'id']},
            {'name': 'schema_id_is_deleted', 'table': 'mark', 'columns': ['schema_id', 'is_deleted']},
            {'name': 'id_schema_id_is_deleted', 'table': 'mark', 'columns': ['schema_id', 'is_deleted', 'id']},
            {'name': 'equipment_id_is_deleted', 'table': 'equipment_schema', 'columns': ['equipment_id', 'is_deleted']},
            {'name': 'id_equipment_id_is_deleted', 'table': 'equipment_schema',
             'columns': ['equipment_id', 'is_deleted', 'id']},
            {'name': 'equipment_is_deleted', 'table': 'equipment', 'columns': ['is_deleted', 'id']}
        ]

        logging.info(f"Начинаем создание индексов в БД: {Path(self.engine.url.database).absolute()}")

        # Получаем список всех таблиц в БД
        available_tables = set(inspector.get_table_names())

        with self.engine.begin() as conn:  # Автоматический commit/rollback
            for config in INDEX_CONFIGS:
                table_name = config['table']
                index_name = config['name']

                # Проверяем существование таблицы
                if table_name not in available_tables:
                    logging.warning(f"Таблица {table_name} не существует, пропускаем индекс {index_name}")
                    continue

                # Проверяем существование индекса
                existing_indexes = {idx['name'] for idx in inspector.get_indexes(table_name)}
                if index_name in existing_indexes:
                    logging.warning(f"Индекс  {index_name} уже существует")
                    continue

                # Создаем индекс
                columns = ', '.join(config['columns'])
                try:
                    # Безопасное создание индекса через SQLAlchemy Core
                    logging.info(f"Создаём индекс {index_name}  в таблице {table_name}")

                    start = time.perf_counter()
                    metadata = MetaData()
                    table = Table(table_name, metadata, autoload_with=self.engine)
                    index = Index(
                        index_name,
                        *[getattr(table.c, col) for col in config['columns']],
                    )
                    index.create(bind=conn)

                    end = time.perf_counter()
                    total_seconds = end - start

                    logging.info(
                        f"Успешно создан индекс {index_name} на {columns} в таблице {table_name} ( Время работы: {total_seconds} сек )")
                except Exception as e:
                    logging.error(f"Ошибка при создании индекса {index_name}: {str(e)}", exc_info=True)

        logging.info(f"Завершено создание индексов в БД: {Path(self.engine.url.database).absolute()}")

    def close(self):
        logging.info("Закрытие Базы данных")
        if self.engine:
            self.engine.dispose()  # Закрывает все соединения в пуле
            self.engine = None
            self.SessionLocal = None
