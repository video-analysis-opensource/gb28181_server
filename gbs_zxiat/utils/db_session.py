# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/6/4
from django.contrib.sessions.backends.db import  *



class ApiSessionStore(SessionStore):

    def __init__(self, session_key):
        SessionStore.__init__(self,session_key)
        self.sk = session_key

    def create(self):
        while True:
            self._session_key = self.sk
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return
