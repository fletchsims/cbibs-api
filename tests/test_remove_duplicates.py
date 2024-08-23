import pandas as pd
import pytest
from sqlalchemy import Column, String, create_engine, MetaData, Table, Integer, FLoat, TIMESTAMP

from app.helpers import remove_duplicates


@pytest.fixture()
def sample_table():
    return pd.DataFrame(
        {
            'col_one': [1, 2, 3, 4, 4],
            'timestamp': pd.to_datetime(['2023-01-01', '2024-02-01', None, '2024-06-01', '2024-06-01']),
            'col_three': ["abc", "def", "ghi", "jkl", "jkl"],
            'col_four': [1.1, 2.2, 3.3, 4.4, 4.4]
        }
    )


@pytest.fixture
def setup_table(engine, sample_table):
    """Fixture to set up the table in the test database."""
    metadata = MetaData()
    table = Table('test_table', metadata,
                  Column('col_one', Integer, primary_key=True),
                  Column('timestamp', TIMESTAMP),
                  Column('col_three', String),
                  Column('col_four', FLoat)
                  )
    metadata.create_all(engine)
    sample_table.to_sql('test_table', engine, if_exists='append', index=False)
    return table


@pytest.fixture
def engine():
    """Fixture to provide a SQLAlchemy engine."""
    return create_engine('sqlite:///:memory:')


def test_remove_duplicates():
    pass
