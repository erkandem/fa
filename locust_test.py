"""
 $ locust -f locust_test.py --host=http://0.0.0.0:5000
"""
import random
from datetime import datetime as dt, timedelta
from locust import HttpLocust, TaskSet, task
from tests.sample_user_agents import ua_strings
from src.const import prices_etf_sym_choices
import os
import json
import dotenv


dotenv.load_dotenv(dotenv.find_dotenv())
CREDS = json.loads(os.getenv('DEFAULT_API_SUPER_USER'))
local_host = 'https://api.volsurf.com'
local_host = 'http://0.0.0.0:5000'


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

    def on_start(self):
        auth_header = get_auth_header(CREDS, self.client)
        self.headers['User-Agent'] = random.choices(ua_strings)[0]
        self.headers = {**self.headers, **auth_header}

    @task(1)
    def index(self):
        url = '/prices/intraday?symbol={}&iunit={}&interval={}&dminus={}'.format(
            random.choice(prices_etf_sym_choices),
            random.choice(['minutes']),
            random.choice([1, 10]),
            random.choice([5, 10, 15, 30, 365])
        )
        self.client.get(url)

    @task(2)
    def curve(self):
        self.client.get('/pulse', headers=self.headers)

    @task(3)
    def single(self):
        params = {
            'symbol': 'cl',
            'nthcontract': random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        }
        self.client.get('/prices/eod/conti', headers=self.headers, params=params)

    @task(4)
    def curve_multiple(self):
        start_date = dt.now() - timedelta(days=random.SystemRandom().randint(1, 365 * 3))
        delta = (dt.now() - start_date).days
        end_date = start_date + timedelta(days=random.SystemRandom().randint(1, delta))
        params = {
            'symbol': 'cl',
            'startdate': start_date.date().strftime('%Y%m%d'),
            'enddate': end_date.date().strftime('%Y%m%d'),
        }
        self.client.get(
            f'/prices/eod/conti/array',
            headers=self.headers,
            params=params
        )


class WebsiteUser(HttpLocust):
    host = local_host
    task_set = WebsiteTasks
    min_wait = 1000
    max_wait = 2000


print('http://localhost:8089')
