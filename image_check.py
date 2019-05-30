import requests
import base64
import json
import os
import sys
from bs4 import BeautifulSoup
from retry import retry
import time

#クラスの作成
class image_information:
    def __init__(self,image,image_base64,google_vison_api_json,item_code):
        self._image = image
        self._image_base64 = image_base64
        self._google_vison_api_json = google_vison_api_json
        self._item_code

    @property
    def image(self):
        return self._image

    @property
    def image_base64(self):
        return self._image_base64

    @property
    def google_vison_api_json(self):
        return self._google_vison_api_json

    @property
    def item_code(self):
        return self._item_code


def get_json_from_googlecloud_vision_api(image_base64):
    GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    # プロキシ突破
    os.environ.get('HTTP_PROXY')

    api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = json.dumps({
        'requests': [{
            'image': {
                # bytes型のままではjsonに変換できないのでstring型に変換する
                'content': image_base64.decode('utf-8')
            },
            'features': [
                {
                    'type': 'IMAGE_PROPERTIES',
                },
                {
                    'type': 'SAFE_SEARCH_DETECTION',
                }
            ]
        }]
    })
    res = requests.post(api_url, data=req_body)
    return res.json()

@retry(tries=3, delay=2, backoff=2)
def return_scraping_html_array(lpm_url,max_page):
    return_array = []
    pg = '&resultCount=100&page='
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    }

    for count in range(max_page):#無限ループにならないように、最大繰り返し回数を指定
        print(str(count + 1) + 'ページ目')
        try:
            soup = BeautifulSoup(requests.get(lpm_url + pg + str(count+1)).content,'html5lib')
        except requests.exceptions.ConnectionError:
            print('NewtorkError')
        except requests.exceptions.TooManyRedirects:
            print('TooManyRedirects')
        except requests.exceptions.HTTPError:
            print('BadResponse')

        for inner_box in soup.find_all(class_="innerBox"):
            for img in inner_box.find_all('img'):
                item_code = get_item_code_from_href(inner_box.a.get('href'))
                url,extension = get_url_exclude_extension(img.get("src"))

                #検索ページの商品画像URLから3L画像のURLを取得
                url_3L = url[:-1] + "3L" + extension
                array = [item_code,url_3L]
                return_array.append(array)

        #次へボタンがなかったら終了
        if bool(soup.find(class_='nextBtn')) == False:
            return return_array

        time.sleep(2)


def is_rule_001():  # 全L1画像共通加工ルール    背景色白の基本パターン    画像サイズ    縦：600px 横：600px
    # def is_rule_001(vision_api_json) -> vision_apiのjsonをつかう場合は、こう書く
    return False


def is_rule_002():  # 全L1画像共通加工ルール    背景色白の基本パターン    容量    50kb以下
    return False


def is_rule_003():  # 全L1画像共通加工ルール 背景色白の基本パターン 解像度 72dpi
    return False


def is_rule_004():
    return False

# 以下 is_rule_*** をつくっていってください



def main():
    lpm_url = "https://lohaco.jp/store/irisplaza/ksearch/?categoryLl=55"
    max_page = 100
    scraping_html_arrya  = return_scraping_html_array(lpm_url,max_page)


    img_base64 = img_to_base64('./sample.jpg')
    googlecloud_vision_json = get_json_from_googlecloud_vision_api(img_base64)

    print('is_rule_001', is_rule_001())

    print('is_rule_002', is_rule_002())

    print('is_rule_003', is_rule_003())


if __name__ == '__main__':
    main()
    sys.exit()
