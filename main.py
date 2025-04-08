import datetime
import os
import time
from io import BytesIO, StringIO
from typing import Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from aws_utils import s3_put_object
from decorators import track_args
from t212 import T212ApiClient


def get_input_dt() -> str:
    current_dt = datetime.date.today()
    previous_month_dt = current_dt - relativedelta(months=1)
    previous_month_dt_str = previous_month_dt.strftime('%Y-%m')

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{previous_month_dt_str}" by ENTER.')
    input_dt_str = input()

    if not input_dt_str:
        input_dt_str = previous_month_dt_str

    return input_dt_str


def get_first_day_of_month(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(day=1)


def get_first_day_of_next_month(dt: datetime.datetime) -> datetime.datetime:
    next_month_dt = dt + relativedelta(months=1)  # works even for Jan and Dec
    return next_month_dt.replace(day=1)


@track_args
def decode_df(encoded_df: bytes, **kwargs) -> pd.DataFrame:
    return pd.read_csv(StringIO(encoded_df.decode('utf-8')), **kwargs)


@track_args
def encode_df(df: pd.DataFrame, **kwargs) -> bytes:
    bytes = BytesIO()
    df.to_csv(bytes, **kwargs)
    bytes.seek(0)
    return bytes.getvalue()


@track_args
def transform(report_df: pd.DataFrame) -> pd.DataFrame:
    ticker_blacklist: list[str] = [
        'VNTRF',  # due to stock split
        'BRK.A',  # not available in digrin
    ]

    ticker_map: dict[str, str] = {
        'VWCE': 'VWCE.DE',
        'VUAA': 'VUAA.DE',
        'SXRV': 'SXRV.DE',
        'ZPRV': 'ZPRV.DE',
        'ZPRX': 'ZPRX.DE',
        'MC': 'MC.PA',
        'ASML': 'ASML.AS',
        'CSPX': 'CSPX.L',
        'EISU': 'EISU.L',
        'IITU': 'IITU.L',
        'IUHC': 'IUHC.L',
        'NDIA': 'NDIA.L',
    }

    # Filter only buys and sells
    report_df = report_df[report_df['Action'].isin(['Market buy', 'Market sell'])]

    # Filter out blacklisted tickers
    report_df = report_df[~report_df['Ticker'].isin(ticker_blacklist)]

    # Apply the mapping to the ticker column
    report_df['Ticker'] = report_df['Ticker'].replace(ticker_map)

    # convert dtypes
    return report_df.convert_dtypes()


def main():
    load_dotenv(override=True)

    bucket_name: str = os.getenv('BUCKET_NAME')

    input_dt_str: str = get_input_dt()  # used later in the naming of csv
    input_dt: datetime.datetime = datetime.datetime.strptime(input_dt_str, '%Y-%m')

    from_dt: datetime.datetime = get_first_day_of_month(input_dt)
    to_dt: datetime.datetime = get_first_day_of_next_month(input_dt)

    t212_client = T212ApiClient(api_key=os.getenv('T212_API_KEY'))

    while True:
        report_id: int = t212_client.create_report(from_dt, to_dt)

        if report_id:
            break

        # limit 1 call per 30s
        time.sleep(10)

    # optimized wait time for report creation
    time.sleep(10)

    while True:
        # reports: list of dicts with keys:
        #   reportId, timeFrom, timeTo, dataIncluded, status, downloadLink
        reports: list[dict[str, Any]] = t212_client.fetch_reports()

        # too many calls -> fetch_reports returns None
        if not reports:
            # limit 1 call per 1min
            time.sleep(10)
            continue

        # filter report by report_id, start from the last report
        report: dict = next(
            filter(lambda report: report.get('reportId') == report_id, reports[::-1])
        )

        if report.get('status') == 'Finished':
            download_link: str = report.get('downloadLink')
            break

    response: requests.Response = requests.get(download_link)

    if response.status_code != 200:
        print(f'{response.status_code=}')
        return

    t212_df_encoded: bytes = response.content
    filename: str = f'{input_dt_str}.csv'
    s3_put_object(bytes=t212_df_encoded, bucket=bucket_name, key=f't212/{filename}')

    t212_df: pd.DataFrame = decode_df(t212_df_encoded)

    digrin_df: pd.DataFrame = transform(t212_df)
    digrin_df.to_csv(filename, index=False)

    digrin_df_encoded: bytes = encode_df(digrin_df, index=False)
    s3_put_object(digrin_df_encoded, bucket=bucket_name, key=f'digrin/{filename}')


if __name__ == '__main__':
    main()
