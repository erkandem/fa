"""
 $ locust -f locust_test.py --host=http://0.0.0.0:5000
"""
import dotenv
from datetime import(
    datetime as dt,
    timedelta,
)
import json
import os
import random

from locust import (
    HttpUser,
    TaskSet,
    task,
)

from tests.sample_user_agents import ua_strings
from src.const import prices_etf_sym_choices


dotenv.load_dotenv(dotenv.find_dotenv())
CREDS = json.loads(os.getenv('DEFAULT_API_SUPER_USER'))


# which full URL to run against (i.e. sth like the base URL)
HOST = 'https://api.volsurf.com'
HOST = 'http://0.0.0.0:5000'

# bypass login just
# TODO: Debug this out, so that login works
TOKEN = ""


def get_auth_header(creds, local_client):
    body = {'username': creds['username'], 'password': creds['password']}
    login_header = {'Content-Type': 'application/x-www-form-urlencoded'}
    login_response = local_client.post('/login', data=body, headers=login_header)
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        header = {'Authorization': f'Bearer {token}'}
        return header
    else:
        print(login_response.status_code)
        print(login_response.json())
        raise ValueError


class WebsiteTasks(TaskSet):
    headers = {'Accept': 'application/json'}

    def _check_and_get_token(self):
        if not TOKEN:
            raise ValueError('Login manually and copy the TOKEN, until login is debugged')
        return TOKEN

    def on_start(self):
        self.headers['User-Agent'] = random.choices(ua_strings)[0]
        self.headers['Authorization'] = f'Bearer {self._check_and_get_token()}'

    @task(3)
    def heartbeat(self):
        self.client.get('/heartbeat', headers=self.headers)

    @task(1)
    def index(self):
        url = '/prices/intraday?symbol={}&iunit={}&interval={}&dminus={}'.format(
            random.choice(prices_etf_sym_choices),
            random.choice(['minutes']),
            random.choice([5, 10]),
            random.choice([5])
        )
        self.client.get(url, headers=self.headers)

    @task(3)
    def single(self):
        params = {
            'symbol': 'cl',
            'nthcontract': random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        }
        self.client.get('/prices/eod/conti', headers=self.headers, params=params)

    @task(1)
    def curve_multiple(self):
        start_date = dt.now() - timedelta(days=random.SystemRandom().randint(10, 20))
        delta = (dt.now() - start_date).days
        end_date = start_date + timedelta(days=random.SystemRandom().randint(1, delta))
        params = {
            'symbol': 'cl',
            'startdate': start_date.date().strftime('%Y-%m-%d'),
            'enddate': end_date.date().strftime('%Y-%m-%d'),
        }
        self.client.get(
            f'/prices/eod/conti/array',
            headers=self.headers,
            params=params
        )


class WebsiteUser(HttpUser):
    host = HOST
    tasks = [
        WebsiteTasks,
    ]
    min_wait = 500
    max_wait = 2000


print('server running at: http://localhost:8089')
print('\n\n!Ey Hombre!\n?Requests are failing?\nDid you check the TOKEN is fresh eh?\n\n')
