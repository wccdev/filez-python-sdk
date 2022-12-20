#!/usr/bin/env python
"""Tests for `demo_project` package."""

import pytest

from filez.calculations import add, divide, multiply, subtract


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_add():
    a = 1
    b = 2
    assert 3 == add(a, b)


def test_subtract():
    a = 1.0
    b = 2.0
    assert -1.0 == subtract(a, b)


def test_multiply():
    a = 2.0
    b = 5.0
    assert 10.0 == multiply(a, b)


def test_divide():
    a = 3
    b = 2
    assert 1.5 == divide(a, b)


def test_divide_zero():
    a = 3
    b = 0
    try:
        divide(a, b)
    except Exception as e:
        assert isinstance(e, ZeroDivisionError)
