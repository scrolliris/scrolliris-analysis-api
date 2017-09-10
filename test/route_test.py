# pylint: disable=invalid-name
"""Unit test for routes
"""
import pytest


@pytest.fixture(autouse=True)
def setup(config):  # pylint: disable=unused-argument
    """The setup
    """

def test_routing_to_humans_txt(dummy_app):
    """Test Routing /humans.txt.
    """
    res = dummy_app.get('/humans.txt', status=200)
    assert 200 == res.status_code


def test_routing_to_robots_txt(dummy_app):
    """Test Routing /robots.txt.
    """
    res = dummy_app.get('/robots.txt', status=200)
    assert 200 == res.status_code
