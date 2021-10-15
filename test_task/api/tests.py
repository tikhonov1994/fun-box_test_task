import time
import unittest
from django.test import Client
from parameterized import parameterized
from api.views import clean_links, remove_not_unique

POST_URL = '/visited_links'
GET_URL = '/visited_domains'
c = Client()


class TestFunctions(unittest.TestCase):
    def test_clean_url(self):
        link_list = [
            'url.ru', 'https://url.ru', 'http://url.ru',
            'url.ru/some_page/', 'url.ru/', 'url.ru/?getparam=0',
            'url.ru?getparam=0', 'http://url.ru/some_page?getparam=0',
        ]
        self.assertEqual(
            clean_links(link_list),
            ['url.ru' for i in range(len(link_list))]
            )

        link_with_symbols = [
            'https://u-r-l.ru/', 'https://u_r_l.ru/',
        ]
        self.assertEqual(clean_links(link_with_symbols), ['u-r-l.ru'])

        not_link_list = [
            'nonlink.', '.notlink', 'n.o.t.l.i.n.k', 'notlink',
        ]
        self.assertEqual(clean_links(not_link_list), [])

    def test_unique_url(self):
        link_list = [
            'url.ru', 'url.ru', 'theurl.ru', 'url.ru',
        ]
        self.assertEqual(len(remove_not_unique(link_list)), 2)


class TestApi(unittest.TestCase):
    def test_wrong_methods(self):
        response = c.get(POST_URL)
        self.assertEqual(response.status_code, 404)
        response = c.post(GET_URL)
        self.assertEqual(response.status_code, 404)

    def test_check_post_errors(self):
        inputs = [
            None,  # full empty
            {},  # empty json
            b'{link: [[}',  # wrong json
            b'[]',  # non_json
        ]
        for data in inputs:
            response = c.post(POST_URL, data, content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_post_no_links(self):
        json_input = {'links': []}
        json_output = {'status': 'ok'}

        response = c.post(POST_URL, json_input,
                          content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), json_output)

    def test_save_links(self):
        json_input = {
            'links': [
                'https://ya.ru',
                'https://ya.ru?q=123',
                'funbox.ru',
                'stackoverflow.com/questions/11828270/how-to-exit-the-vim'
                '-editor ',
            ],
        }
        json_output = {'status': 'ok'}

        response = c.post(POST_URL, json_input,
                          content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), json_output)

    def test_get_empty_links(self):
        json_output = {'status': 'ok', 'domains': []}

        response = c.get(GET_URL + '?from=0&to=1',
                         content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_output)

    @parameterized.expand([
        (None, None),
        ('from=10', None),
        (None, 'to=10'),
        ('from=', 'to='),
        ('from=10', 'to='),
        ('from=', 'to=10'),
        ('from=a', 'to=b'),
    ])
    def test_check_get_errors(self, start, end):
        response = c.get(
            GET_URL + '?{0}&{1}'.format(start, end),
            content_type='application/json',
            )
        self.assertEqual(response.status_code, 400)

    def test_post_and_get_links(self):
        json_input = {
            'links': [
                'https://ya.ru',
                'https://ya.ru?q=123',
                'funbox.ru',
                'stackoverflow.com/questions/11828270/how-to-exit-the-vim'
                '-editor ',
            ],
        }
        curr_time = round(time.time())

        # post
        response = c.post(POST_URL, json_input,
                          content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # get
        response = c.get(
            GET_URL + '?from={}&to={}'.format(curr_time, curr_time+200),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        domains = response.json()['domains']
        self.assertIn('ya.ru', domains)
        self.assertIn('funbox.ru', domains)
        self.assertIn('stackoverflow.com', domains)
        self.assertEquals(domains.count('ya.ru'), 1)

        # get somewhere after
        response = c.get(
            GET_URL + '?from={}&to={}'.format(
                curr_time + 200, curr_time + 500
                ),
            content_type='application/json',
        )
        self.assertEquals(response.status_code, 200)
        domains = response.json()['domains']
        self.assertNotIn('ya.ru', domains)
        self.assertNotIn('funbox.ru', domains)
        self.assertNotIn('stackoverflow.com', domains)
