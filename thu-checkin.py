#!/usr/bin/env python3

import configparser
import io
import os
import PIL
import pytesseract
import re
import requests

# https://stackoverflow.com/a/35504626/5958455
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


print("Tsinghua University Daily Health Report")

dirname = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(dirname, "thu-checkin.txt"))
data = config["thu-checkin"]

juzhudi = data["RESIDENCE"]
emergency_name = data["EMERGENCY_NAME"]
emergency_relation = data["EMERGENCY_RELATION"]
emergency_mobile = data["EMERGENCY_MOBILE"]
school_abbr = data["SCHOOL_ABBR"]
user_agent = data.get("USER_AGENT", "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0")

CAS_LOGIN_URL = f"https://passport.{school_abbr}.edu.cn/login"
CAS_CAPTCHA_URL = f"https://passport.{school_abbr}.edu.cn/validatecode.jsp?type=login"
CAS_RETURN_URL = f"https://weixine.{school_abbr}.edu.cn/2020/caslogin"
HOME_URL = f"https://weixine.{school_abbr}.edu.cn/2020/home"
REPORT_URL = f"https://weixine.{school_abbr}.edu.cn/2020/daliy_report"
# Not my fault:                                            ^^


def parse_token(s: str) -> str:
    x = re.search(r"""<input.*?name="_token".*?>""", s).group(0)
    return re.search(r'value="(\w*)"', x).group(1)


def make_session() -> requests.Session:
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers["User-Agent"] = user_agent
    return s


def login(s: requests.Session) -> requests.Response:
    r = s.get(CAS_LOGIN_URL, params={"service": CAS_RETURN_URL})
    cas_lt = re.search(r'<input.*?name="CAS_LT".*?value="(LT-\w*)".*?>', r.text).group(1)

    r = s.get(CAS_CAPTCHA_URL)
    img = PIL.Image.open(io.BytesIO(r.content))
    pix = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pix[i, j]
            if g >= 40 and r < 80:
                pix[i, j] = (0, 0, 0)
            else:
                pix[i, j] = (255, 255, 255)
    lt_code = pytesseract.image_to_string(img).strip()

    payload = {
        "model": "uplogin.jsp",
        "service": CAS_RETURN_URL,
        "warn": "",
        "showCode": "1",
        "username": username,
        "password": password,
        "button": "",
        "CAS_LT": cas_lt,
        "LT": lt_code,
    }
    return s.post(CAS_LOGIN_URL, data=payload)


def checkin(s: requests.Session) -> bool:
    r = s.get(HOME_URL)
    payload = {
        "_token": parse_token(r.text),
        "juzhudi": juzhudi,
        "body_condition": "1",
        "body_condition_detail": "",
        "has_fever": "0",
        "last_touch_sars": "0",
        "last_touch_sars_date": "",
        "last_touch_sars_detail": "",
        "is_danger": "0",
        "is_goto_danger": "0",
        "jinji_lxr": emergency_name,
        "jinji_guanxi": emergency_relation,
        "jiji_mobile": emergency_mobile,
        "other_detail": "",
    }

    r = s.post(REPORT_URL, data=payload)

    # Fail if not 200
    r.raise_for_status()

    # Fail if not reported
    checkin_success = r.text.find("上报成功") >= 0
    return checkin_success


def get_auth_data():
    pass


if __name__ == "__main__":
    username, password = get_auth_data()
    s = make_session()
    login(s)
    assert checkin(s)
