# pylint: disable=invalid-name
import pytest


@pytest.fixture(autouse=True)
def setup(config):  # pylint: disable=unused-argument
    """The setup
    """
    pass


def test_connection_states_for_assets(dummy_app, mocker):
    """Test db connection state opening for assets request
    """
    from scythia.request import CustomRequest, db
    mocker.spy(CustomRequest, 'open_db')
    mocker.spy(CustomRequest, 'close_db')

    assert db.is_closed()

    dummy_app.get('/humans.txt', status=200)

    # pylint: disable=no-member
    assert 0 == CustomRequest.open_db.call_count
    assert 0 == CustomRequest.close_db.call_count
    assert db.is_closed()


def test_connection_states_for_healthcheck(dummy_app, mocker):
    """Test db connection state opening for health check request
    """
    from scythia.request import CustomRequest, db
    mocker.spy(CustomRequest, 'open_db')
    mocker.spy(CustomRequest, 'close_db')

    assert db.is_closed()

    dummy_app.get('/_ah/health', status=404)

    # pylint: disable=no-member
    assert 0 == CustomRequest.open_db.call_count
    assert 0 == CustomRequest.close_db.call_count
    assert db.is_closed()


def test_connection_states_for_api(dummy_app, mocker):
    """Test db connection state opening for api request
    """
    from scythia.request import CustomRequest, db
    mocker.spy(CustomRequest, 'open_db')
    mocker.spy(CustomRequest, 'close_db')

    assert db.is_closed()

    dummy_app.get('/v1.0/projects/1/results/read', status=403)

    # pylint: disable=no-member
    assert 1 == CustomRequest.open_db.call_count
    assert 1 == CustomRequest.open_db.call_count
    assert db.is_closed()
