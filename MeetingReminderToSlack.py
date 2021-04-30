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

# from dotenv import load_dotenv
# load_dotenv()

def get_200_response(message):
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def lambda_handler(event, context):
    # holiday decision
    now = datetime.date.today()
    today = str(now.year) + "/" + str(now.month) + "/" + str(now.day)
    if is_holiday(today):
        return get_200_response('Today is a holiday.')

    ############################################################
    # Zoom
    ############################################################
    join_url = get_meeting_url()
    
    ############################################################
    # Slack
    ############################################################
    slack_url = "https://slack.com/api/chat.postMessage"
    slack_token = os.environ['SLACK_BOT_TOKEN']
    slack_headers = {
        "content-type": "application/json; charset=utf-8",
    	"Authorization": "Bearer " + slack_token
    }
    slack_obj = {
    	"token"		:	slack_token,
    	# "channel"	:	os.environ['SLACK_CHANNEL_TEST'],	#crd-test
    	"channel"	:	os.environ['SLACK_CHANNEL_MAIN'],	#crd-circas
        "text"		:	"<!channel>【Meeting】リマインダー : 朝会9:40～　夕会17:00～　\n　ZoomUrl : " + join_url,
    }
    slack_params = json.dumps(slack_obj).encode("utf-8")
    req = urllib.request.Request(slack_url,slack_params,slack_headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    print(body)

    return get_200_response('ok')

############################################################
# Zoom
############################################################
def get_meeting_url():
    ZOOM_API_KEY = os.environ['ZOOM_API_KEY']
    ZOOM_API_SECRET = os.environ['ZOOM_API_SECRET']
    ZOOM_USER_ID = os.environ['ZOOM_USER_ID']

    expiration = int(time.time()) + 5 # 5sec
    header    = base64.urlsafe_b64encode('{"alg":"HS256","typ":"JWT"}'.encode()).replace(b'=', b'') 
    payload   = base64.urlsafe_b64encode(('{"iss":"'+ZOOM_API_KEY+'","exp":"'+str(expiration)+'"}').encode()).replace(b'=', b'') # APIキーと>有効期限
    hashdata  = hmac.new(ZOOM_API_SECRET.encode(), header+".".encode()+payload, hashlib.sha256) # HMACSHA256でハッシュを作成
    signature = base64.urlsafe_b64encode(hashdata.digest()).replace(b'=', b'') # ハッシュをURL-Save Base64でエンコード
    zoom_token = (header+".".encode()+payload+".".encode()+signature).decode()  # トークンをstrで生成
    conn = http.client.HTTPSConnection("api.zoom.us")
    zoom_headers = {
        'authorization': "Bearer "+ zoom_token,
        'content-type': "application/json; charset=utf-8"
    }
    open_time = (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
    zoom_obj = {
        "topic": "Meeting",
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
    zoom_url = "https://api.zoom.us/v2/users/" + ZOOM_USER_ID + "/meetings"
    conn.request("POST", zoom_url, zoom_params, zoom_headers)
    res = conn.getresponse()
    data = res.read()
    dic = json.loads(data.decode("utf-8"))
    return dic["join_url"]

############################################################
# 祝日判定（today：YYYY/MM/DD）
############################################################
def is_holiday(today):
    url = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
    with urllib.request.urlopen(url) as res:
        mem = res.read()

    holidays = {}
    for row in mem.decode('cp932').splitlines():
        arr = row.split(",")
        day, name = arr[0], arr[1]
        holidays[day] = {'day': day, 'name': name}

    # 年末年始定休日
    add_company_holiday(holidays, '2020/12/29')
    add_company_holiday(holidays, '2020/12/30')
    add_company_holiday(holidays, '2020/12/31')
    add_company_holiday(holidays, '2021/1/2')
    add_company_holiday(holidays, '2021/1/3')
    add_company_holiday(holidays, '2021/1/4')
    add_company_holiday(holidays, '2021/4/30')
    add_company_holiday(holidays, '2021/12/29')
    add_company_holiday(holidays, '2021/12/30')
    add_company_holiday(holidays, '2021/12/31')
    add_company_holiday(holidays, '2022/1/2')
    add_company_holiday(holidays, '2022/1/3')
    add_company_holiday(holidays, '2022/1/4')

    return today in holidays

def add_company_holiday(holidays, day):
    holidays[day] = {'day': day, 'name': '定休日'}

if __name__ == "__main__":
    res = lambda_handler({},{})
    print(res)
