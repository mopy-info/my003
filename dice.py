"pylint に docstring を書けと言われた"
import os
import configparser
import logging
import random
from collections import OrderedDict
import datetime
import numpy as np
from flask import Flask, request, Response


def is_digit_or_float(s):
    "pylint に docstring を書けと言われた"
    rtnval = False
    try:
        ss = int(s)
        rtnval = True
    except ValueError:
        pass
    try:
        ss = float(s)
        rtnval = True
    except ValueError:
        pass
    return rtnval


def shake(number_of_face):
    "pylint に docstring を書けと言われた"
    return int(random.randrange(1, number_of_face+1))


def dttm():
    "pylint に docstring を書けと言われた"
    n = datetime.datetime.today()
    rtntxt = n.strftime('%Y%m%d') + '_'
    rtntxt += n.strftime('%H%M%S') + '_'
    rtntxt += str(n.microsecond)
    return rtntxt


config = configparser.ConfigParser()
config.read('config.ini')

if os.path.exists(config.get('logging', 'name')):
    os.remove(config.get('logging', 'name'))

fmt = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=config.get('logging', 'level'),
                    filename=config.get('logging', 'name'),
                    format=fmt)
logger = logging.getLogger(config.get('logging', 'logger'))
logger.info("dice start")

app = Flask(__name__, static_folder=".", static_url_path='')


@app.route('/')
def home():
    "pylint に docstring を書けと言われた"
    return 'sorry no service'


@app.route('/dice')
def dice():
    "pylint に docstring を書けと言われた"
    rtncd = 0
    number_of_dice = -1
    number_of_face = -1
    times = -1

    if is_digit_or_float(request.args.get('nod', '1')):
        number_of_dice = int(request.args.get('nod', '1'))
    else:
        rtncd = 1

    if is_digit_or_float(request.args.get('nof', '6')):
        number_of_face = int(request.args.get('nof', '6'))
    else:
        rtncd = 2

    if is_digit_or_float(request.args.get('times', '1')):
        times = int(request.args.get('times', '1'))
    else:
        rtncd = 3

    if rtncd == 0:
        if number_of_dice < 1 or number_of_dice > 1024:
            rtncd = 1
        if number_of_face < 1 or number_of_face > 1024:
            rtncd = 2
        if times < 1 or times > 1024:
            rtncd = 3

    if rtncd == 0:
        time_cnt = 0
        ttl = 0
        min = 1025 * 1025
        max = 0
        deme = np.zeros((times, number_of_dice), dtype=int)
        zorome = np.zeros((times, number_of_face), dtype=int)

        while time_cnt < times:
            number_of_dice_cnt = 0
            sttl = 0
            while number_of_dice_cnt < number_of_dice:
                crtval = shake(number_of_face)
                ttl += crtval
                sttl += crtval
                deme[time_cnt, number_of_dice_cnt] = crtval
                zorome[time_cnt, crtval-1] += 1
                number_of_dice_cnt += 1
            if min > sttl:
                min = sttl
            if max < sttl:
                max = sttl
            time_cnt += 1

    result = OrderedDict(rtncd=str(rtncd))

    if rtncd == 0:
        result['ttl'] = str(ttl)
        result['zoro'] = str(0)
        result['avg'] = str(ttl / times)
        result['min'] = str(min)
        result['max'] = str(max)
        demeflnm = 'deme' + dttm() + '_' + str(random.randrange(1, 1000000))
        np.savetxt("deme/" + demeflnm, deme, fmt='%d', delimiter=',')
        result['deme'] = demeflnm

    rtntxt = '{'
    for i in result:
        if len(rtntxt) == 1:
            pass
        else:
            rtntxt = rtntxt + ','
        if is_digit_or_float(result[i]):
            rtntxt = rtntxt + ' "' + i + '": ' + result[i]
        else:
            rtntxt = rtntxt + ' "' + i + '": "' + result[i] + '"'
    rtntxt = rtntxt + ' }'

    return rtntxt


@app.route('/deme')
def deme():
    "pylint に docstring を書けと言われた"
    if os.path.exists("deme/" + request.args.get('flnm')):
        with open("deme/" + request.args.get('flnm'), 'rt') as fin:
            rtntxt = fin.read()
        return rtntxt
    else:
        response = Response()
        response.status_code = 404
        return response


if config.getboolean('debug', 'mode'):
    app.run(port=config.getint('service', 'port'),
            debug=config.getboolean('debug', 'mode'))
else:
    app.run(port=config.getint('service', 'port'),
            host='0.0.0.0',
            debug=config.getboolean('debug', 'mode'))
