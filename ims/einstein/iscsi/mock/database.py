from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

import constants as mock_constants
import ims.common.config as config
import ims.exception.db_exceptions as db_exceptions

_cfg = config.get()


class Database:
    def __init__(self):
        self.__connection = DatabaseConnection()
        self.target = TargetRepository(self.__connection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.__connection.close()


# It is responsible for creating and closing sessions
class DatabaseConnection:
    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()

    # Refer Issue in BMI's database.py for moving engine into __init__
    # The other reason is db_path is being used without validating it

    # creates all tables if not present
    def __init__(self):
        engine = create_engine(
            'sqlite:///' + _cfg.iscsi[mock_constants.MOCK_DB_PATH_KEY],
            poolclass=SingletonThreadPool)
        session_maker = sessionmaker(bind=engine)
        DatabaseConnection.Base.metadata.create_all(engine)
        self.session = session_maker()

    def close(self):
        self.session.close()


class TargetRepository:
    def __init__(self, connection):
        self.connection = connection

    # inserts the arguments into the table
    def insert(self, name):
        try:
            target = Target()
            target.name = name
            self.connection.session.add(target)
            self.connection.session.commit()
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)

    # deletes target with name
    def delete_with_name(self, name):
        try:
            project = self.connection.session.query(Target).filter_by(
                name=name).one_or_none()
            if project is not None:
                self.connection.session.delete(project)
                self.connection.session.commit()
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)

    def fetch_targets(self):
        try:
            targets = self.connection.session.query(Target)
            return [target.name for target in targets]
        except SQLAlchemyError as e:
            raise db_exceptions.ORMException(e.message)


class Target(DatabaseConnection.Base):
    __tablename__ = "target"
    name = Column(String, primary_key=True, nullable=False)
