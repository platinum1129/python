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

if __name__ == "__main__":
    
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
        'content-type': "application/json"
    }
    # open_time = (datetime.datetime.today() + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
    # zoom_obj = {
    #     "topic": "Meeting",
    #     "type": 2,	#1:即時 2:時間指定（時間指定でないとホスト抜き不可）
    #     "start_time": open_time,
    #     "timezone": "Asia/Tokyo",
    #     "settings": {
    #         "host_video" : "false",
    #         "participant_video" : "false",
    #         "join_before_host" : "true",
    #         "use_pmi": "false",
    #         "approval_type" : "0",
    #         "waiting_room" : "false"
    #     }
    # }
    # zoom_params = json.dumps(zoom_obj).encode("utf-8")

    # ZOOM_USER_ID = "matsumoto@corerd.co.jp"
    ZOOM_USER_ID = "platinum1129@hotmail.com"
    
    zoom_url = "https://api.zoom.us/v2/users/" + ZOOM_USER_ID
    conn.request("GET", zoom_url, headers=zoom_headers)
    res = conn.getresponse()
    data = res.read()
    res.close()
    
    dic = json.loads(data.decode("utf-8"))
    
    print(res.status)
    print(res.reason)
    print(data.decode("utf-8"))
