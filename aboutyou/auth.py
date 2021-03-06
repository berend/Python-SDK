#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import requests

from .config import Config


class AuthException(Exception):
    pass


class Auth(object):
    """
    This class wraps the Api user authorization interface.

    :param credentials: The app credentials.
    :param config: The app configuration.
    """
    def __init__(self, credentials, config=Config()):
        self.credentials = credentials
        self.config = config

    def login_url(self, redirect):
        """
        Generates the login url.

        :param appid: The app id for which context the user will should generate an access token.
        :param redirect: An url to which the browser will be redirected after login.
        :param shop_url: *Optional* The url to the login.

        .. note::

            Besure that the redirect url is registered in the devcenter!
        """
        url = self.config.shop_url + "?client_id="
        url += str(self.credentials.app_id) + "&redirect_uri="
        url += redirect + "&response_type=token&scope=firstname id lastname email"

        return url


    def get_me(access_token):
        """
        Returns the user information to the corresponding Api access token.

        :param access_token: The access token retreived from the login.
        :raises AuthException: If the reuqests results in an error.
        """
        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "User-Agent": self.config.agent,
            "Authorization": "Bearer {}".format(access_token)
        }

        response = requests.get("https://oauth.collins.kg/oauth/api/me",
                                headers=headers,
                                verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            raise AuthException(response.content)


    def get_access_token(email, password, redirect):
        """
        A dirty hack to get an access token right away.

        This function fakes an webbrowser and a user which logins
        on the Api website.

        :param email: The email of an user.
        :param password: The corresponding password.
        :param redirect: The redirect url to use.
        :returns: <access_token>, <token_type>
        :raises AuthException: If an request error occours.
        """
        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "User-Agent": self.config.agent,
        }

        session = requests.Session()
        response = session.get(login_url(self.credentials.app_id, redirect), headers=headers)

        if response.status_code != 200:
            raise AuthException(response.content)

        url = self.config.shop_url + '/login'
        data = {'LoginForm[email]': email, 'LoginForm[password]': password}
        params = {'avstdef': 2, 'client_id': 110, 'redirect_uri': redirect,
                    'scope': 'firstname+id+lastname+email', 'response_type': 'token'}
        response = session.post(url, data=data, params=params, headers=headers)

        if response.status_code == 200:
            data = response.url.split('#')[1]
            values = dict((x.split('=') for x in data.split('&')))

            return values['access_token'], values['token_type']
        else:
            raise AuthException(response.content)
