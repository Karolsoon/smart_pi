import pytest
from mockito import when, mock, unstub


def test_wifi_is_connected():
    ...


def test_lcd_is_cinnected():
    ...


def test_bmp280_is_connected():
    ...


def test_raises_exception_when_no_lcd_connected():
    ...


def test_raises_exception_when_no_bmp280_connected():
    ...


def test_raises_exception_when_wifi_is_not_connected():
    ...


def test_lcd_thread_is_restarted_after_failure():
    ...


def test_lcd_thread_failure_is_logged_in_log_file():
    ...


def test_thread_failure_log_format():
    # Column number, information template, delimiter, timestamp format
    ...