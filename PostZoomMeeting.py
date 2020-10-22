import os
import json
import time
import hmac
import http.client
import base64
import urllib
import urllib.request
import logging
import hashlib
import datetime

# from dotenv import load_dotenv
# load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_OAUTH_TOKEN = os.environ['SLACK_OAUTH_TOKEN']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_USER_NAME = os.environ['SLACK_USER_NAME']
ZOOM_API_KEY = os.environ['ZOOM_API_KEY']
ZOOM_API_SECRET = os.environ['ZOOM_API_SECRET']
ZOOM_USER_ID = os.environ['ZOOM_USER_ID']

def lambda_handler(event, context):

    #受信したjsonをLogsに出力
    logging.info(json.dumps(event))

    # Slackからのリトライの場合は処理無視
    if 'x-slack-retry-num' in event.get('headers'):
        return {'statusCode': 200}

    # json処理
    if 'body' in event:
        body = json.loads(event.get('body'))
    elif 'token' in event:
        body = event
    else:
        logger.error('unexpected event format')
        return {'statusCode': 500, 'body': 'error:unexpected event format'}
    
    if 'challenge' in body:
        challenge = body.get('challenge')
        return {
            'statusCode': 200,
            'body': json.dumps({
            	'challenge' : challenge
            })
        }
    
    #SlackMessageに「zoom」が入っている場合
    body_text = body.get('event').get('text')
    logging.info("body_text:" + body_text)
    if 'zoom' in body_text.lower(): # ignore-case
        host_user = get_email(body.get('event').get('user'))
        logging.info("host_user:" + host_user)
        join_url = get_meeting_url(host_user)
        logging.info("join_url:" + join_url)

        ts = None
        if 'thread_ts' in body.get('event'):
            # thread_ts は スレッドのルート
            ts = body.get('event').get('thread_ts')
        else:
            # スレッド中からの呼び出しじゃないと、thread_tsは無いので、tsを指定
            ts = body.get('event').get('ts')

        url = 'https://slack.com/api/chat.postMessage'
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(SLACK_BOT_TOKEN)
        }
        data = {
            'token': SLACK_BOT_TOKEN,
            'channel': body.get('event').get('channel'),
            'text': 'ZoomUrl : ' + join_url,
            'username': SLACK_USER_NAME,
            'thread_ts': ts
        }
        # POST処理　
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST', headers=headers)
        res = urllib.request.urlopen(req)
        logger.info('post result: %s', res.msg)
        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({
                'text' : "OK",
                'join_url' : join_url
            })
        }
        
    return {
        'statusCode': 200,
        'headers': {},
        'body': "noting"
    }


def get_email(slack_user_id):
    logging.info("slack_user_id:"+ slack_user_id)
    slack_token = os.environ['SLACK_BOT_TOKEN']
    slack_url = "https://slack.com/api/users.info?token=" + slack_token + "&user=" + slack_user_id
    req = urllib.request.Request(slack_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()

    dic = json.loads(body.decode("utf-8"))
    email = dic["user"]["profile"]["email"]
    logging.info("email:"+ email)

    return email

############################################################
# Zoom
############################################################
def get_meeting_url(host_user):
    
    if isWithinTheTeam(host_user):
        zoom_user_id = host_user        # Zoomのチーム内であれば自身をホスト
    else:
        zoom_user_id = ZOOM_USER_ID     # Zoomのチーム外であればデフォルトをホスト
    
    open_time = (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
    zoom_obj = {
        "topic": zoom_user_id + " Meeting",
        "type": 2,	#1:即時 2:時間指定（時間指定でないとホスト抜き不可）
        "start_time": open_time,
        "timezone": "Asia/Tokyo",
        "settings": {
            "host_video" : "false",
            "participant_video" : "false",
            "join_before_host" : "true",
            "use_pmi": "false",
            "approval_type" : "0",
            "waiting_room" : "false"
        }
    }
    zoom_params = json.dumps(zoom_obj).encode("utf-8")

    zoom_url = "https://api.zoom.us/v2/users/" + zoom_user_id + "/meetings"    
    conn = http.client.HTTPSConnection("api.zoom.us")
    conn.request("POST", zoom_url, zoom_params, headers=get_zoom_headers())
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    logging.info(data)
    dic = json.loads(data)
    return dic["join_url"]


def isWithinTheTeam(zoom_user_id):
    zoom_url = "https://api.zoom.us/v2/users/" + zoom_user_id
    conn = http.client.HTTPSConnection("api.zoom.us")
    conn.request("GET", zoom_url, headers=get_zoom_headers())
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    res.close()
    logging.info(data)
    logging.info(res.status)
    return res.status == 200


def get_zoom_headers():
    expiration = int(time.time()) + 5 # 5sec
    header = base64.urlsafe_b64encode('{"alg":"HS256","typ":"JWT"}'.encode()).replace(b'=', b'') 
    payload = base64.urlsafe_b64encode(('{"iss":"'+ZOOM_API_KEY+'","exp":"'+str(expiration)+'"}').encode()).replace(b'=', b'') # APIキーと>有効期限
    hashdata = hmac.new(ZOOM_API_SECRET.encode(), header+".".encode()+payload, hashlib.sha256) # HMACSHA256でハッシュを作成
    signature = base64.urlsafe_b64encode(hashdata.digest()).replace(b'=', b'') # ハッシュをURL-Save Base64でエンコード
    zoom_token = (header+".".encode()+payload+".".encode()+signature).decode()  # トークンをstrで生成
    zoom_headers = {
        'authorization': "Bearer "+ zoom_token,
        'content-type': "application/json"
    }
    return zoom_headers


if __name__ == "__main__":
    lambda_handler({
        "token": "testtoken",
        "challenge": "testchallenge",
        "type": "url_verification"
    },
    {})
