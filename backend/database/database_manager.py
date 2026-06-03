from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path


class DatabaseManager:

    def __init__(self):

        self.engine = None

        self.db_type = None

    # =====================================
    # SQLITE
    # =====================================

    def connect_sqlite(self, db_path: str):

        db_path = Path(db_path)

        connection_string = f"sqlite:///{db_path}"

        self.engine = create_engine(connection_string)

        self.db_type = "sqlite"

    # =====================================
    # POSTGRESQL
    # =====================================

    def connect_postgresql(
        self,
        host,
        port,
        database,
        username,
        password
    ):

        connection_string = (
            f"postgresql://{username}:{password}"
            f"@{host}:{port}/{database}"
        )

        self.engine = create_engine(connection_string)

        self.db_type = "postgresql"

    # =====================================
    # MYSQL
    # =====================================

    def connect_mysql(
        self,
        host,
        port,
        database,
        username,
        password
    ):

        connection_string = (
            f"mysql+pymysql://{username}:{password}"
            f"@{host}:{port}/{database}"
        )

        self.engine = create_engine(connection_string)

        self.db_type = "mysql"

    # =====================================
    # CSV
    # =====================================

    def connect_csv(self, csv_path: str):

        csv_path = Path(csv_path)

        df = pd.read_csv(csv_path)

        sqlite_path = csv_path.with_suffix(".db")

        sqlite_engine = create_engine(
            f"sqlite:///{sqlite_path}"
        )

        df.to_sql(
            "uploaded_csv_data",
            sqlite_engine,
            if_exists="replace",
            index=False
        )

        self.engine = sqlite_engine

        self.db_type = "csv"

    # =====================================
    # GET ENGINE
    # =====================================

    def get_engine(self):

        return self.engine