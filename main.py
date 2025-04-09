import os
import time
from datetime import date, datetime
from typing import Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from custom_utils import aws_utils, csv_utils, datetime_utils, decorators, t212_utils


@decorators.track_args
def get_input_dt() -> str:
    current_dt = date.today()
    previous_month_dt = current_dt - relativedelta(months=1)
    previous_month_dt_str = previous_month_dt.strftime('%Y-%m')

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{previous_month_dt_str}" by ENTER.')
    input_dt_str = input()

    if not input_dt_str:
        input_dt_str = previous_month_dt_str

    return input_dt_str


@decorators.track_args
def transform(report_df: pd.DataFrame) -> pd.DataFrame:
    # Filter only buys and sells
    allowed_actions: list[str] = ['Market buy', 'Market sell']
    report_df = report_df[report_df['Action'].isin(allowed_actions)]

    # Filter out blacklisted tickers
    ticker_blacklist: list[str] = [
        'VNTRF',  # due to stock split
        'BRK.A',  # not available in digrin
    ]
    report_df = report_df[~report_df['Ticker'].isin(ticker_blacklist)]

    # Apply the mapping to the ticker column
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
    report_df['Ticker'] = report_df['Ticker'].replace(ticker_map)

    # convert dtypes
    return report_df.convert_dtypes()


def main():
    load_dotenv(override=True)

    bucket_name: str = os.getenv('BUCKET_NAME')

    input_dt_str: str = get_input_dt()  # used later in the naming of csv
    input_dt: datetime = datetime.strptime(input_dt_str, '%Y-%m')

    from_dt: datetime = datetime_utils.get_first_day_of_month(input_dt)
    to_dt: datetime = datetime_utils.get_first_day_of_next_month(input_dt)

    t212_client = t212_utils.ApiClient(api_key=os.getenv('T212_API_KEY'))

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
    aws_utils.s3_put_object(
        bytes=t212_df_encoded, bucket=bucket_name, key=f't212/{filename}'
    )

    t212_df: pd.DataFrame = csv_utils.decode_to_df(t212_df_encoded)
    t212_df.to_csv(f't212_{filename}', index=False)

    digrin_df: pd.DataFrame = transform(t212_df)
    digrin_df.to_csv(filename, index=False)

    digrin_df_encoded: bytes = csv_utils.encode_df(digrin_df)
    aws_utils.s3_put_object(
        digrin_df_encoded, bucket=bucket_name, key=f'digrin/{filename}'
    )


if __name__ == '__main__':
    main()
