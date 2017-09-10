def test_vars():
    """
    Returns env var names to update in testing

    These values are updated with values prefixed as `TEST_`.
    See .env.sample.
    """
    return [
        'DOMAIN',
        'WSGI_URL_SCHEME',
        'RESPONSE_PREFIX',
        'DATABASE_URL',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'DYNAMODB_ENDPOINT_URL',
        'DYNAMODB_REGION_NAME',
        'DYNAMODB_TABLE_NAME',
    ]
