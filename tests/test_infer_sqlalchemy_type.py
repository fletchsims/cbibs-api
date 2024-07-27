import pandas as pd
from sqlalchemy import String, Integer, Float, TIMESTAMP

from app.helpers import infer_sqlalchemy_type


def test_infer_sqlalchemy_type():
    assert infer_sqlalchemy_type(pd.Series([1]).dtype) == Integer
    assert infer_sqlalchemy_type(pd.Series([1.0]).dtype) == Float
    assert infer_sqlalchemy_type(pd.Series(pd.to_datetime(['2020-01-01'])).dtype) == TIMESTAMP
    inferred_type = infer_sqlalchemy_type(pd.Series(['string']).dtype)
    assert isinstance(inferred_type, String) and inferred_type.length == 255
