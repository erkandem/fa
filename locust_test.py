"""
 $ locust -f locust_test.py --host=http://0.0.0.0:5000
"""
import random
from datetime import datetime as dt, timedelta
from locust import HttpLocust, TaskSet, task
from tests.sample_user_agents import ua_strings
from falib.const import prices_etf_sym_choices


local_host = 'http://localhost:5000'


class WebsiteTasks(TaskSet):
    headers = {'Accept': 'application/json'}

    def on_start(self):
        self.headers['User-Agent'] = random.choices(ua_strings)[0]
        return

    @task(1)
    def index(self):
        url = '/prices/intraday?symbol={}&iunit={}&interval=1&dminus={}'.format(
            random.choice(prices_etf_sym_choices),
            random.choice(['minutes', 'hour', 'day']),
            random.randint(10, 15)
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
