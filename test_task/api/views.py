import json
import re
import time
from urllib.parse import urlparse

import redis
from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
                         JsonResponse)
from django.views.decorators.csrf import csrf_exempt

from test_task.settings import REDIS_HOST, REDIS_PORT

url_regex = re.compile(
    r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.[a-zA-Z]{2,}$')
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def clean_links(links_list):
    clean_list = []
    for index in range(len(links_list)):
        link = links_list[index]
        parsed = urlparse(link)
        link = parsed.netloc or parsed.path
        link = link.split('/')[0]
        if re.match(url_regex, link) is not None:
            clean_list.append(link)
    return clean_list


def remove_not_unique(links_list):
    if len(links_list) > 0:
        links_list.sort()
        unique_links = [links_list[0]]
        i, j = 1, 0
        while i < len(links_list):
            if unique_links[j] != links_list[i]:
                unique_links.append(links_list[i])
                j += 1
            i += 1
        return unique_links
    return links_list


@csrf_exempt
def save_links(request):
    if request.method == 'POST':
        try:
            content = json.loads(request.body)
            cleaned_links = clean_links(content['links'])
            unique_links = remove_not_unique(cleaned_links)

            if unique_links:
                curr_time = round(time.time())
                r.sadd(curr_time, *unique_links)

            return JsonResponse(data={'status': 'ok'}, status=201)
        except KeyError:
            return JsonResponse(data={'status': 'List "links" cant be empty!'},
                                status=400)
        except Exception as e:
            return HttpResponseBadRequest(content=e)
    return JsonResponse(data={'status': 'Response not found'}, status=404)


@csrf_exempt
def get_domains(request):
    if request.method == 'GET':
        try:
            start_time = int(request.GET.get('from'))
            end_time = int(request.GET.get('to')) + 1
            links = set()

            for curr_time in range(start_time, end_time):
                if r.smembers(str(curr_time)):
                    links.update(r.smembers(str(curr_time)))

            domains = [link.decode('utf-8') for link in links]
            return JsonResponse(
                data={'domains': domains,
                      'status': 'ok'},
                status=200,
            )
        except Exception as e:
            return HttpResponseBadRequest(content=e)
    return HttpResponseNotFound()
