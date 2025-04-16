import dataframe_utils
import pandas as pd

default_df: pd.DataFrame = pd.DataFrame({'name': ['Adam', 'Eva'], 'userid': [10, 11]})
default_bytes: bytes = b'name,userid\nAdam,10\nEva,11\n'


def test_decode_csv() -> None:
    assert default_df.equals(dataframe_utils.decode_to_df(default_bytes))


def test_encode_csv() -> None:
    assert dataframe_utils.encode_df(default_df) == default_bytes
