import pandas as pd
import pytest
from sqlalchemy import MetaData, create_engine
from sqlalchemy.schema import CreateTable

from app.helpers import create_table


@pytest.fixture()
def sample_table():
    return pd.DataFrame(
        {
            'col_one': [1, 2, 3, 4],
            'timestamp': pd.to_datetime(['2023-01-01', '2024-02-01', None, '2024-06-01']),
            'col_three': ["abc", "def", "ghi", "jkl"],
            'col_four': [1.1, 2.2, 3.3, 4.4]
        }
    )


@pytest.fixture()
def metadata():
    return MetaData()


def test_create_table(sample_table, metadata):
    table_name = 'table_name'
    table = create_table(metadata, sample_table, table_name)

    print(CreateTable(table).compile(create_engine('sqlite://')))
    assert table.name == table_name
    assert len(table.columns) == len(sample_table.columns)
    assert all(col.name in sample_table.columns for col in table.columns)
