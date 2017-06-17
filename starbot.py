#encoding:utf-8
from selenium import webdriver
import DatabaseOpe
import sys
import io
import os
import time
from bs4 import BeautifulSoup
import urllib
import re
from selenium.webdriver.common.keys import Keys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


########################################
# 設定値                                #
########################################
# 文字数制限
# この文字数以下はブックマークしない
num = 500
# ブックマークキーワード
# この文字を含む記事のみブックマークする('|'区切りでいくつも設定可能)
key = re.compile(r"バンプ|BUMP|python|Python|PYTHON|プログラム|くりぃむ|作曲|モンハン|モンスターハンター|HUNTER|哲学|ガジェット|webサービス|映画|心理|ソロギター|レビュー")
# はてなユーザー名
user = 'XXXXXX'
# はてなパスワード
passWord = 'XXXXXX'
# スターフラグ
# ブックマークはしたいけど、スターはつけたくない場合とかに使う
# スターをつけたい場合は True
# スターをつけない場合は False
starFlg = True
# ブックマークフラグ
# スターはつけたいけど、ブックマークはしたくない場合とかに使う
# ブックマークしたい場合は True
# ブックマークしたくない場合は False
bookmarkFlg = True
# ダウンロードしたブラウザのパス(ダウンロードしたchromedriver.exeのパスを記入ください)
chromedriver = "XXXXXX"

########################################
# 固定値                                #
########################################
# タグ外し正規表現
p = re.compile(r"<[^>]*?>")
# ログインURL
LoginURL = 'https://www.hatena.ne.jp/login?via=200125'
# 新着記事URL
newURL = 'http://recent.start162432.com/'
# ブックマークURL
bookmark1 = 'http://b.hatena.ne.jp/'
bookmark2 = '/add.confirm?url='

DBpath = os.path.normpath(os.path.join(os.path.abspath(__name__),'../')) + '/DB/hatena.db'
DB = DatabaseOpe.DatabaseOpe(DBpath)

########################################
# メイン                                #
########################################

# ブラウザ設定
browser = webdriver.Chrome(executable_path=chromedriver)
browser.get(LoginURL)

# ユーザー名入力
elementName = browser.find_element_by_name("name")
elementName.send_keys(user)

# パスワード入力
elementPass = browser.find_element_by_name("password")
elementPass.send_keys(passWord)

# エンターキー押下
elementPass.send_keys(Keys.ENTER)
# ログインするまで待機
time.sleep(3)


# タグ生成関数
def getTag(datas):
    temp1 = ''
    for temp in datas:
        if temp1.find(temp) == -1:
            temp1 = temp1 + '[' + str(temp) + ']'
    return temp1

# 無限ループ
while True:
    # 新着記事一覧取得
    html = urllib.request.urlopen(newURL).read()
    soup = BeautifulSoup(html, "html.parser")
    ac = soup.find_all("a", class_="blog-title")
    # 新着記事数分回す
    for a in ac:
        try:
            # タイトルとURL取得
            temp = str(a)
            temp1 = temp[28:len(temp)-6].split('"')
            url = temp1[0][:len(temp1[0])-1]
            title = temp1[3][1:]

            # 記事ごとにステータス表示
            print('---------------------------', flush=True)
            print(title, flush=True)
            print(url, flush=True)

            # ブログ本文取得
            html = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            honbun = soup.find_all("div", class_="entry-content")

            # htmlタグ外し
            hon = p.sub("", str(honbun[0]))

            # 観覧済みフラグ取得
            cnt = DB.getBlogs(url)

            # 本文表示
            print(len(hon), flush=True)

            # 観覧済みなら何もしない
            if int(cnt) > 0:
                print("すでに観覧済み", flush=True)

            # 観覧済みじゃないなら記事を解釈
            else:

                # DBに記事内容保存
                seq = DB.getBlogsSeq()
                DB.insertBlogs(seq,title,url,hon)

                # 本文のキーワードを判定
                MatchObject = re.findall(key, hon)

                # 条件にマッチするならブックマーク&スターをつける
                if len(hon) > num and MatchObject != []:

                    # ブックマーク処理
                    if bookmarkFlg :
                        browser.get(bookmark1 + user + bookmark2 + str(url))

                        # タグ設定
                        print(str(getTag(MatchObject)), flush=True)
                        elementComment = browser.find_element_by_name("comment")
                        elementComment.send_keys(str(getTag(MatchObject)))

                        # ブックマーク
                        time.sleep(1)
                        elementComment.send_keys(Keys.ENTER)
                        time.sleep(2)

                    if starFlg :
                        # スター処理
                        browser.get(url)
                        time.sleep(5)
                        elementStar = browser.find_element_by_class_name("hatena-star-add-button")
                        elementStar.send_keys(Keys.ENTER)
                        time.sleep(5)

                    print("ブックマーク&スター完了", flush=True)
                else:
                    print("ブックマーク&スターしない", flush=True)
        except:
            # 例外処理(クラス名でスターをつけてるので、スターのクラスを変更されていると、ここに入ることが多いが大体スターをつけられるのでよしとする。)
            print(sys.exc_info(), flush=True)
            print("ブックマーク&スター失敗", flush=True)
        print('---------------------------', flush=True)
    # 新着記事500件を一周したら5待機
    # 5分くらいなら、投稿の多い時間でもなんとかなるっぽい？
    time.sleep(300)
