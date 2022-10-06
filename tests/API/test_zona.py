import requests
import threading

import pytest
from mockito import when, mock, unstub

from API.secrets import IP, PORT
from API.app import zona
from GPIO.lcdprinter import LCDPrinter


# LCD = LCDPrinter(0x27)


# @pytest.fixture(scope='module')
# def root():
#     yield f'http://{IP}:{PORT}/'


# @pytest.fixture(scope='function')
# def zona_response():
#     text = 'lorem.ipsum.karol'
#     when(LCD).write(...).thenReturn(None)
#     response = mock(
#         {
#             'status_code': 200,
#             'text': zona(text)
#         },
#         spec=requests.Response
#     )
#     return response


# def test_threads_response_code(root, zona_response):
#     when(requests).get(root + 'zona').thenReturn(zona_response)
#     response = requests.get(root + 'zona')
#     assert response.status_code == 200
#     unstub()


# def test_threads_response_text(root, zona_response):
#     when(requests).get(root + 'zona').thenReturn(zona_response)
#     response = requests.get(root + 'zona')
#     assert response.text == 'lorem ipsum karol'
#     unstub()
