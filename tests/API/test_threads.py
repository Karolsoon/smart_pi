import requests
import threading

import pytest
from mockito import when, mock, unstub

from API.secrets import IP, PORT
from API.app import threads


@pytest.fixture(scope='module')
def root():
    yield f'http://{IP}:{PORT}/'


@pytest.fixture(scope='function')
def threads_response():
    threads_list = [
        threading.Thread(name='lcd_thread'),
        threading.Thread(name='Thread-1'),
        threading.Thread(name='MainThread')
        ]
    when(threading).enumerate().thenReturn(threads_list)
    response = mock(
        {
            'status_code': 200,
            'text': threads()
        },
        spec=requests.Response
    )
    return response


def test_threads_response_code(root, threads_response):
    when(requests).get(root + 'threads').thenReturn(threads_response)
    response = requests.get(root + 'threads')
    assert response.status_code == 200
    unstub()


def test_threads_response_text(root, threads_response):
    when(requests).get(root + 'threads').thenReturn(threads_response)
    response = requests.get(root + 'threads')
    assert response.text == "['lcd_thread', 'Thread-1', 'MainThread']"
    unstub()
