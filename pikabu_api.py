#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 16:01:42 2017

@author: fisherman
"""

import requests
import json

import logging
logging.basicConfig(format = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level = logging.DEBUG,
                    filename = 'pikabu_api.log')

# Some dirty hack...
logging.critical("JUST END OF LOG!!!\n\n\n\nNEW LOG\n")


"""
Abstract class. Parent of other pikabu classes.
"""
class PikabuApi():
    settings = {}
    state = {}
    request_info = {}
    session = None
    
    def set_session(self, s):
        logging.info("New session obj: " + str(s))
        self.session = s
        
    def get_session(self):
        return self.session
    
    
    def __init__(self, login, password, session_obj = requests.Session()):
        self.session = session_obj
        
        self.settings["login"] = str(login)
        self.settings["password"] = str(password)
        
        
        self.state["is_logged"] = False
        
        self.request_info["base_url"] = "http://pikabu.ru/"
        self.request_info["auth_url"] = self.request_info["base_url"] + "ajax/auth.php"
        self.request_info["default_headers"] = { 
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.75 Safari/537.36}",
                "Referer": "http://pikabu.ru",
                "Host": "pikabu.ru"
                }
        self.request_info["default_post_headers"] = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "application/json, text/javascript, */*; q=0.01"
                }
        logging.info("Abstract created for " + str(login))
        
    def fill_session_info(self):
        self.session.get(self.request_info["base_url"],
                             headers=self.request_info["default_headers"])
        self.request_info["default_post_headers"]['X-Csrf-Token'] = self.session.cookies.get_dict()["PHPSESS"]
        
        
    def sign_in(self):
        self.fill_session_info()
        login_data = {
                    "username": self.settings["login"],
                    "password": self.settings["password"],
                    "mode": "login"
                    }
            
        headers = self.request_info["default_headers"]
        headers.update(self.request_info["default_post_headers"])
            
        logging.debug("Sending POST for " + str(self.settings["login"]))
        response = self.session.post(self.request_info["auth_url"],
                                 data = login_data,
                                 headers = headers)
        resp_body = json.loads(response.text)
            
        logging.debug(str(resp_body))
        if str(resp_body["result"]).upper() != "TRUE":
            logging.error("Can`t sign in")
            logging.debug(str(self.settings["login"]) + ":" + str(self.settings["password"]))
            
            try:
                if (resp_body['data']["need_captha"].upper() == "TRUE"):
                    logging.error("Captcha is needed!")
                    raise Exception("Captcha is needed!")
            except KeyError:
                logging.error('Key "need_captha" not exist')
                raise Exception("Can`t sign in")                
        else:
            self.state["is_logged"] = True
                
        
    def sign_out(self):
        self.fetch_url("ajax/logout.php", need_auth = False)
    
    """
    Makes a request to self.request_info["base_url"] + url
    Logs in if not logged (check need_auth)
    """
    def fetch_url(self, url, data=None, method='POST', need_auth=True):
        if url is None:
            logging.error("Url is None. Wtf?")
            raise Exception("Url is None. Wtf?")
        
        if (not self.state["is_logged"] and need_auth):
            self.sign_in()   
        else:
            if not self.request_info["default_post_headers"].has_header('X-Csrf-Token'):
                self.fill_session_info()
                
        url = self.request_info["base_url"] + url
        logging.info("Requesting " + url + " " + method)
        if "POST" == method:
            headers = self.request_info["default_headers"]
            headers.update(self.request_info["default_post_headers"])
            response = self.session.post(url,
                                         data = data,
                                         headers = headers)
        elif "GET" == method:
            headers = self.request_info["default_headers"]
            response = self.session.get(url,
                                        headers = headers,
                                        params = data)
        return response
            
    def rait_post(self, action, post_id):
        logging.info("Seting " + str(action) + " to " + str(post_id))
        if action != '+' and action != '-':
            logging.error("Bad action " + str(action))
            raise Exception("Bad action " + str(action))
        act = (0, 1)["+" == action]
        d = {"story_id": post_id,
             "vote": act}
        resp = self.fetch_url("ajax/vote_story.php", data = d)
        return resp
    
    
    
