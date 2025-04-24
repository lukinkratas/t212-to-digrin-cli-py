import datetime
from typing import Any

import requests

from custom_utils import decorators


class APIClient(object):
    def __init__(self, key: str):
        self.key = key

    @decorators.track_args
    def create_report(
        self,
        from_dt: str | datetime.datetime,
        to_dt: str | datetime.datetime,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions: bool = True,
    ) -> int | None:
        """Spawns T212 csv export process.

        Args:
            start_dt - start as datetime or string format %Y-%m-%dT%H:%M:%SZ
            end_dt - end as datetime or string format %Y-%m-%dT%H:%M:%SZ

        Returns:
            reportId of the created report if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        if isinstance(from_dt, datetime.datetime):
            from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        if isinstance(to_dt, datetime.datetime):
            to_dt = to_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        payload = {
            'dataIncluded': {
                'includeDividends': include_dividends,
                'includeInterest': include_interest,
                'includeOrders': include_orders,
                'includeTransactions': include_transactions,
            },
            'timeFrom': from_dt,
            'timeTo': to_dt,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.key,
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            decorators.logger.warning(f'{response.status_code=}')
            return None

        return response.json().get('reportId')

    @decorators.track_args
    def list_reports(self) -> list[dict[str, Any]] | None:
        """Fetches list of reports.

        Returns:
            list of dicts of report attributes if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        headers = {'Authorization': self.key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            decorators.logger.warning(f'{response.status_code=}')
            return None

        return response.json()


class Report(object):
    def __init__(
        self,
        reportId: int,  # noqa: N803
        timeFrom: str,  # noqa: N803
        timeTo: str,  # noqa: N803
        dataIncluded: dict[str, bool],  # noqa: N803
        status: str,
        downloadLink: str,  # noqa: N803
    ):
        self.report_id = reportId
        self.time_from = timeFrom
        self.time_to = timeTo
        self.data_included = dataIncluded
        self.status = status
        self.download_link = downloadLink

    @decorators.track_args
    def download(self) -> bytes | None:
        response = requests.get(self.download_link)

        if response.status_code != 200:
            decorators.logger.warning(f'{response.status_code=}')
            return None

        return response.content
