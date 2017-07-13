#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import sys
import logging

from flask import Flask, render_template
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/webhook', methods=['POST'])

def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    if req.get("result").get("action") != "bookMyConference":
        return {}

    #oauth
    orequest = req.get("originalRequest") # work down the tree
    odata = orequest.get("data") # work down the tree
    user = odata.get("user") # work down the tree
    access_token = user.get("access_token")

    #data
    result = req.get("result") # work down the tree
    parameters = result.get("parameters") # work down the tree
    startdate = parameters.get("start-date")
    meetingname = parameters.get("meeting-name")

    payload = {
        "start-date": startdate,
        "end-date": startdate,
        "meeting-name": meetingname
    }

   # POST info to join.me
    baseurl = "https://api.join.me/v1/meetings"
    headers = { 
              'content-type': 'application/json',
               'authorization': 'Bearer ' + access_token
             }
    result = requests.post(baseurl, data=json.dumps(payload), headers=headers)
    data = result.json()
    print(data)
    res = makeWebhookResult(data)
    return res

def makeWebhookResult(data):

    speech = "Appointment scheduled!"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "source": "heroku-bookmyconference"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
