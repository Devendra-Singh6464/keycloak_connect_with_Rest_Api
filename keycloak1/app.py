import json
import logging
import os

from flask import Flask, g
from flask_oidc import OpenIDConnect
import requests
from keycloak import KeycloakOpenID
from oauth2client.client import OAuth2Credentials

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'TpuAEMd2qWVwfNsM6TevLOGmaljrgPeQ',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'auth.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    # 'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    # 'OIDC_EMAIL_VERIFICATION' = 'mandatory',
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'flask_app',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
    # 'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer'
})
print(os.listdir())
os.chdir("/home/deepak/keycloak1")

oidc = OpenIDConnect(app)

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8081/",
                                 client_id="rest_api",
                                 realm_name="flask_app",
                                 client_secret_key="TpuAEMd2qWVwfNsM6TevLOGmaljrgPeQ")

@app.route('/')
@oidc.require_login
def protected():
    info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
    username = info.get('preferred_username')
    email = info.get('email')
    sub = info.get('sub')
    print("""user: %s, email:%s"""%(username, email))

    token = oidc.get_access_token()
    return ("""%s"""%token)


@app.route('/private', methods=['POST'])
@oidc.accept_token(require_token=True)
def hello_api():
    return("""user: %s, email:%s"""%(g.oidc_token_info['username'], g.oidc_token_info['preferred_username']))


@app.route('/logout')
def logout():
    """Performs local logout by removing the session cookie."""
    refresh_token = oidc.get_refresh_token()
    oidc.logout()
    if refresh_token is not None:
        keycloak_openid.logout(refresh_token)
    oidc.logout()
    g.oidc_id_token = None
    return 'Hi, you have been logged out! <a href="/">Return</a>'


if __name__ == '__main__':
    app.run()
