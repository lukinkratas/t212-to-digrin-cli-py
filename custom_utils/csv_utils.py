from io import BytesIO, StringIO

import pandas as pd


def decode_to_df(encoded_df: bytes, **kwargs) -> pd.DataFrame:
    return pd.read_csv(StringIO(encoded_df.decode('utf-8')), **kwargs)


def encode_df(decoded_df: pd.DataFrame, **kwargs) -> bytes:
    index = kwargs.pop('index', False)
    bytes = BytesIO()
    decoded_df.to_csv(bytes, index=index, **kwargs)
    bytes.seek(0)
    return bytes.getvalue()
