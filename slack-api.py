import http.client
import base64
import time
import hmac
import hashlib
import urllib
import json
import urllib.request
import datetime
import os

from dotenv import load_dotenv
load_dotenv()

def lambda_handler(event, context):
    
    ############################################################
    # Slack
    ############################################################
    
    slack_token = os.environ['SLACK_BOT_TOKEN']
    slack_headers = {
        "content-type": "application/json; charset=utf-8",
    	"Authorization": "Bearer " + slack_token
    }
    slack_obj = {
    	"token"		:	slack_token,
    	# "channel"	:	os.environ['SLACK_CHANNEL_TEST'],	#crd-test
    	"channel"	:	os.environ['SLACK_CHANNEL_MAIN'],	#crd-circas
        "text"		:	"<!channel>【Meeting】リマインダー : 朝会9:40～　夕会17:00～　\n　ZoomUrl : "
    }
    slack_params = json.dumps(slack_obj).encode("utf-8")
    slack_url = "https://slack.com/api/users.info?token=" + slack_token + "&user=USXDBD4LW"
    # slack_url = "https://slack.com/api/users.list?token=" + slack_token
    req = urllib.request.Request(slack_url, slack_params, slack_headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    print(body)

    dic = json.loads(body)

    print(dic["user"]["profile"]["email"])

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == "__main__":
    lambda_handler({},{})
