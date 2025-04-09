from io import BytesIO, StringIO

import pandas as pd


def decode_df(encoded_df: bytes, **kwargs) -> pd.DataFrame:
    return pd.read_csv(StringIO(encoded_df.decode('utf-8')), **kwargs)


def encode_df(df: pd.DataFrame, **kwargs) -> bytes:
    bytes = BytesIO()
    df.to_csv(bytes, **kwargs)
    bytes.seek(0)
    return bytes.getvalue()
