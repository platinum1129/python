import urllib.request
import json


url = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
holidays = {}

# 祝日ファイルダウンロード（ファイル）
# savename = "syukujitsu.csv"
# urllib.request.urlretrieve(url, savename)
# with open(savename, encoding="cp932", newline='') as f:
#     reader = csv.reader(f)
#     next(reader)  # CSVのヘッダーを飛ばす
#     for row in reader:
#         day, name = row[0], row[1]
#         holidays[day] = {'day': day, 'name': name}

# 祝日ファイルダウンロード（メモリ）
with urllib.request.urlopen(url) as res:
    mem = res.read()

for row in mem.decode('cp932').splitlines():
    arr = row.split(",")
    day, name = arr[0], arr[1]
    holidays[day] = {'day': day, 'name': name}
    
# 辞書を for 文の繰り返し用変数として使用すると、変数にはキーが入る
# for key in holidays:

# 結果出力
for key, val in holidays.items():
    day = val['day']
    name = val['name']
    print(f'{day} {name}')



