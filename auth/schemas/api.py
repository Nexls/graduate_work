from flask_restplus import Api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

api = Api(
    None,
    version='1.0',
    title='Auth API',
    description='Auth API документация',
    doc='/api/docs/',
    default='Auth API',
    authorizations=authorizations
)
