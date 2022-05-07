import urllib
import json
import urllib.request
import datetime
import os

#from dotenv import load_dotenv
#load_dotenv()

#EventBridge (CloudWatch Events): Jobcan-attend
#Cron 式 30 23 ? * MON-FRI *
#EventBridge (CloudWatch Events): Jobcan-leave
#Cron 式 30 8 ? * MON-FRI *

def get_200_response(message):
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def lambda_handler(event, context):
    
    # holiday decision
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')  # UTCから9時間差の「JST」タイムゾーン
    now = datetime.datetime.now(JST)  # タイムゾーン付きでローカルな日付と時刻を取得
    print(now)
    today = str(now.year) + "/" + str(now.month) + "/" + str(now.day)
    if is_holiday(today):
        return get_200_response('Today is a holiday.')

    # Button Message
    buttontext = ''
    if now.hour < 12:
        buttontext = '出　勤'
    else:
        buttontext = '退　勤'

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
    	#"channel"	:	os.environ['SLACK_CHANNEL_TEST'],	#crd-test
    	#"channel"	:	os.environ['SLACK_CHANNEL_MAIN'],	#crd-circas
    	"channel"	:	os.environ['SLACK_CHANNEL_JOBCAN'],	#crd-jobcan
        "text"		:	"<!channel>リマインダー : ジョブカンで「" + buttontext + "」を忘れずに！ https://id.jobcan.jp/users/sign_in",
    }
    slack_params = json.dumps(slack_obj).encode("utf-8")
    req = urllib.request.Request(slack_url,slack_params,slack_headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    print(body)

    return get_200_response('ok')

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
    add_company_holiday(holidays, '2023/1/2')
    add_company_holiday(holidays, '2023/1/3')
    add_company_holiday(holidays, '2023/1/4')

    return today in holidays

def add_company_holiday(holidays, day):
    holidays[day] = {'day': day, 'name': '定休日'}

if __name__ == "__main__":
    res = lambda_handler({},{})
    print(res)
