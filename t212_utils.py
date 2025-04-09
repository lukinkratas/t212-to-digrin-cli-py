import datetime
from typing import Any

import requests

from decorators import track_args


class T212ApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @track_args
    def create_report(
        self, from_dt: str | datetime.datetime, to_dt: str | datetime.datetime
    ) -> int | None:
        """
        Spawns T212 csv export process.

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
                'includeDividends': True,
                'includeInterest': True,
                'includeOrders': True,
                'includeTransactions': True,
            },
            'timeFrom': from_dt,
            'timeTo': to_dt,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.api_key,
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(f'{response.status_code=}')
            return None

        return response.json().get('reportId')

    @track_args
    def fetch_reports(self) -> list[dict[str, Any]] | None:
        """
        Fetches list of reports.

        Returns:
            list of dicts of report attributes if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        headers = {'Authorization': self.api_key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f'{response.status_code=}')
            return None

        return response.json()
