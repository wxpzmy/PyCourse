import requests
import string
import random

def random_string_generator(length):
    return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

def login_coursera(user, pwd):

    # using cousera api for login
    signin_url = "https://accounts.coursera.org/api/v1/login"

    login = {"email" : user,
             "password" : pwd,
             "webrequest" : "true"
            }

    user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"

    # generate cookie and csrf token
    xcsrf2cookie = "csrf2_token_%s" % random_string_generator(8)
    xcsrf2token = random_string_generator(24)
    xcsrftoken = random_string_generator(24)
    cookie = "csrftoken=%s; %s=%s" % (xcsrftoken, xcsrf2cookie, xcsrf2token)
    header = {"User-Agent" : user_agent,
              "Referer" : "https://accounts.coursera.org/signin",
              "X-Requested-With" : "XMLHttpRequest",
              "X-CSRF2-Cookie" : xcsrf2cookie,
              "X-CSRF2-Token" : xcsrf2token,
              "X-CSRFToken" : xcsrftoken,
              "Cookie" : cookie
             }

    # use request library to do the post operation
    session = requests.Session()
    ret = session.post(signin_url, data=login, headers=header, verify=True)
   
    if ret.status_code == 200:
       return session
    else:
       raise RuntimeError("Login failed!.")




