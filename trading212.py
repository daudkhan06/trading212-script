
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


class Trading212Client:
    def __init__(self):
        key = os.environ["T212_API_KEY"]
        secret = os.environ["T212_API_SECRET"]

        env = os.getenv("T212_ENV", "live").lower()
        if env not in ("live", "demo"):
            raise ValueError("T212_ENV must be live or demo")

        self.base_url = f"https://{env}.trading212.com"

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(key, secret)

    def _get(self, path):
        """Make a read-only API request."""
        parsed = urlsplit(path)

        if parsed.scheme or parsed.netloc:
            raise ValueError("External URLs are not allowed")

        if not parsed.path.startswith("/api/v0/equity/"):
            raise ValueError("Invalid API endpoint")

        response = self.session.get(
            self.base_url + path,
            timeout=20
        )
        response.raise_for_status()
        return response.json()

    def get_account(self):
        """Retrieve current account summary."""
        return self._get(
            "/api/v0/equity/account/summary"
        )

    def get_positions(self):
        """Retrieve current portfolio holdings."""
        return self._get(
            "/api/v0/equity/positions"
        )

    def get_instruments(self):
        """Retrieve stock and ETF metadata."""
        return self._get(
            "/api/v0/equity/metadata/instruments"
        )

    def get_transactions(self, start_date=None):
        """Retrieve transaction history with pagination."""
        endpoint = "/api/v0/equity/history/transactions"
        path = f"{endpoint}?limit=50"

        transactions = []
        visited = set()

        while path:
            if path in visited:
                raise RuntimeError(
                    "Repeated pagination cursor detected"
                )

            visited.add(path)
            page = self._get(path)
            transactions.extend(page.get("items", []))

            next_path = page.get("nextPagePath")
            if not next_path:
                break

            if next_path.startswith(endpoint + "?"):
                path = next_path
            elif next_path.startswith("?"):
                path = endpoint + next_path
            elif not next_path.startswith("/"):
                path = endpoint + "?" + next_path
            else:
                raise ValueError(
                    "Unexpected pagination path"
                )

            time.sleep(11)

        if start_date is not None:
            transactions = self.filter_transactions(
                transactions, start_date
            )

        return transactions

    @staticmethod
    def filter_transactions(transactions, start_date):
        """Filter transactions by UTC date."""
        if start_date.tzinfo is None:
            raise ValueError(
                "start_date must include timezone information"
            )

        filtered = []

        for transaction in transactions:
            date_string = transaction.get("dateTime")

            if not date_string:
                continue

            transaction_date = datetime.fromisoformat(
                date_string.replace("Z", "+00:00")
            )

            if transaction_date.tzinfo is None:
                transaction_date = transaction_date.replace(
                    tzinfo=timezone.utc
                )

            if transaction_date >= start_date:
                filtered.append(transaction)

        return filtered

    def close(self):
        """Close the HTTP session."""
        self.session.close()
