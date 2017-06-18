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
num = 1000
# ブックマークキーワード
# この文字を含む記事のみブックマークする('|'区切りでいくつも設定可能)
key = re.compile(r"webサービス|モバイル|モンスターハンター|モンハン|PYTHON|Python|python|電気|電子|パーツ|ノートパソコン|PC|スマホ|タブレット|映画|レビュー|感想|BUMP|bump|Bump|バンプ")
# タグ設定
# タグ名:[タグワード]で設定する。
# タグワードを複数指定することができる。
# ++は必須条件。-0はor条件
# 下の例だと記事に「映画」と「レビュー」か「感想」という言葉が入ってる記事を「映画(レビュー)」というタグでブックマーク。
# -0,-1と設定することで XXX AND XXX OR XXX OR XXX AND XXX OR XXX みたいな条件でブックマークできる。
tagset = {"webサービス":["++webサービス"],"モンハン":["-0モンスターハンター","-0モンハン"],"python":["-0PYTHON","-0Python","-0python"],"レビュー(ガッジェット)":["++レビュー","-0モバイル","-0パーツ","-0PC","-0スマホ","-0タブレット","-0電子","-0電気"],"映画":["++映画","-0レビュー","-0感想"],"バンプ":["-0BUMP","-0bump","-0Bump","-0バンプ"]}
# はてなユーザー名
user = 'XXX'
# はてなパスワード
passWord = 'XXX'
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
chromedriver = "XXX"

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
def getTag(tags,datas):
    temp1 = ''
    # タグ数文ループ
    for tag,word in tags.items():
        #リストの場合
        temp2 = []
        Flag = True
        if isinstance(word, list):
            for w in word :
                if w[:2] == '++':
                    if w[2:] not in datas:
                        Flag = False
                        break
                if w[:1] == '-':
                    if (int(w[1:2])+1) != int(len(temp2)):
                        temp2.append(False)
                    if w[2:] in datas:
                        temp2[int(w[1:2])]=True
                if temp2.count(False) > 0:
                    Flag = False
        #1単語の場合
        else :
            if word[2:] not in datas:
                Flag = False
        if Flag :
            temp1 = temp1 + '[' + str(tag) + ']'
    return temp1

def getTagKeyList(datas):
    temp1 = []
    for temp in datas:
        if temp not in temp1:
            temp1.append(str(temp))
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
                tagkey = getTagKeyList(MatchObject)
                inputTag = getTag(tagset,tagkey)

                # 条件にマッチするならブックマーク&スターをつける
                if len(hon) > num and inputTag is not '':

                    # ブックマーク処理
                    if bookmarkFlg :
                        browser.get(bookmark1 + user + bookmark2 + str(url))

                        # タグ設定
                        print(str(inputTag), flush=True)
                        elementComment = browser.find_element_by_name("comment")
                        elementComment.send_keys(str(inputTag))

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
