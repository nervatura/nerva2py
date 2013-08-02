#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Michele Comitini <mcm@glisco.it>
License: GPL v3

Adds support for  OAuth1.0a authentication to web2py.

Dependencies:
 - python-oauth2 (http://github.com/simplegeo/python-oauth2)

"""

import oauth2 as oauth
import cgi

from urllib import urlencode

from gluon import current

class OAuthAccount(object):
    """
    Login will be done via   OAuth Framework, instead of web2py's
    login form.

    Include in your model (eg db.py)::
        # define the auth_table before call to auth.define_tables()
        auth_table = db.define_table(
           auth.settings.table_user_name,
           Field('first_name', length=128, default=""),
           Field('last_name', length=128, default=""),
           Field('username', length=128, default="", unique=True),
           Field('password', 'password', length=256,
           readable=False, label='Password'),
           Field('registration_key', length=128, default= "",
           writable=False, readable=False))

        auth_table.username.requires = IS_NOT_IN_DB(db, auth_table.username)
        .
        .
        .
        auth.define_tables()
        .
        .
        .

        CLIENT_ID=\"<put your fb application id here>\"
        CLIENT_SECRET=\"<put your fb application secret here>\"
        AUTH_URL="..."
        TOKEN_URL="..."
        ACCESS_TOKEN_URL="..."
        from gluon.contrib.login_methods.oauth10a_account import OAuthAccount
        auth.settings.login_form=OAuthAccount(globals(
            ),CLIENT_ID,CLIENT_SECRET, AUTH_URL, TOKEN_URL, ACCESS_TOKEN_URL)

    """

    def __redirect_uri(self, next=None):
        """Build the uri used by the authenticating server to redirect
        the client back to the page originating the auth request.
        Appends the _next action to the generated url so the flows continues.
        """
        r = self.request
        http_host = r.env.http_host

        url_scheme = r.env.wsgi_url_scheme
        if next:
            path_info = next
        else:
            path_info = r.env.path_info
        uri = '%s://%s%s' % (url_scheme, http_host, path_info)
        if r.get_vars and not next:
            uri += '?' + urlencode(r.get_vars)
        return uri

    def accessToken(self):
        """Return the access token generated by the authenticating server.

        If token is already in the session that one will be used.
        Otherwise the token is fetched from the auth server.

        """

        if self.session.access_token:
            # return the token (TODO: does it expire?)

            return self.session.access_token
        if self.session.request_token:
            # Exchange the request token with an authorization token.
            token = self.session.request_token
            self.session.request_token = None

            # Build an authorized client
            # OAuth1.0a put the verifier!
            token.set_verifier(self.request.vars.oauth_verifier)
            client = oauth.Client(self.consumer, token)

            resp, content = client.request(self.access_token_url, "POST")
            if str(resp['status']) != '200':
                self.session.request_token = None
                self.globals['redirect'](self.globals[
                                         'URL'](f='user', args='logout'))

            self.session.access_token = oauth.Token.from_string(content)

            return self.session.access_token

        self.session.access_token = None
        return None

    def __init__(self, g, client_id, client_secret, auth_url, token_url, access_token_url):
        self.globals = g
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = None
        self.request = current.request
        self.session = current.session
        self.auth_url = auth_url
        self.token_url = token_url
        self.access_token_url = access_token_url

        # consumer init
        self.consumer = oauth.Consumer(self.client_id, self.client_secret)

    def login_url(self, next="/"):
        self.__oauth_login(next)
        return next

    def logout_url(self, next="/"):
        self.session.request_token = None
        self.session.access_token = None
        return next

    def get_user(self):
        '''Get user data.

        Since OAuth does not specify what a user
        is, this function must be implemented for the specific
        provider.
        '''
        raise NotImplementedError("Must override get_user()")

    def __oauth_login(self, next):
        '''This method redirects the user to the authenticating form
        on authentication server if the authentication code
        and the authentication token are not available to the
        application yet.

        Once the authentication code has been received this method is
        called to set the access token into the session by calling
        accessToken()
        '''

        if not self.accessToken():
            # setup the client
            client = oauth.Client(self.consumer, None)
            # Get a request token.
            # oauth_callback *is REQUIRED* for OAuth1.0a
            # putting it in the body seems to work.
            callback_url = self.__redirect_uri(next)
            data = urlencode(dict(oauth_callback=callback_url))
            resp, content = client.request(self.token_url, "POST", body=data)
            if resp['status'] != '200':
                self.session.request_token = None
                self.globals['redirect'](self.globals[
                                         'URL'](f='user', args='logout'))

            # Store the request token in session.
            request_token = self.session.request_token = oauth.Token.from_string(content)

            # Redirect the user to the authentication URL and pass the callback url.
            data = urlencode(dict(oauth_token=request_token.key,
                                  oauth_callback=callback_url))
            auth_request_url = self.auth_url + '?' + data

            HTTP = self.globals['HTTP']

            raise HTTP(302,
                       "You are not authenticated: you are being redirected to the <a href='" + auth_request_url + "'> authentication server</a>",
                       Location=auth_request_url)

        return None
