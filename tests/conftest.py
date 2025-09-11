import pytest
import mongomock
from mongoengine import connect, disconnect, get_connection
from app import create_app

TEST_DB_ALIAS = "testdb"
TEST_DB_NAME = "mongoenginetest"

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for testing."""
    app, socketio = create_app("testing")  # unpack both
    return app

@pytest.fixture(scope="session", autouse=True)
def mock_mongo():
    """Use mongomock instead of real MongoDB (session-wide)."""
    connect(
        TEST_DB_NAME,
        host="mongodb://localhost",  # dummy
        mongo_client_class=mongomock.MongoClient,
        alias=TEST_DB_ALIAS
    )
    yield
    disconnect(alias=TEST_DB_ALIAS)

@pytest.fixture(autouse=True)
def clear_db():
    """Clear the in-memory MongoDB after each test."""
    yield
    conn = get_connection(alias=TEST_DB_ALIAS)
    conn.drop_database(TEST_DB_NAME)

@pytest.fixture
def client(app):
    """Flask test client for making requests."""
    return app.test_client()