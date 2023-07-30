# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from pymongo import MongoClient
import re

def extract_username(url):
    # 正規表現パターンを定義します。
    pattern = r"plaza\.rakuten\.co\.jp/([^/]+)/"
    # re.search()関数を使って、入力データからパターンにマッチする部分を抽出します。
    match = re.search(pattern, url)
    if match:
        # マッチした部分（グループ1）を取得して返します。
        return match.group(1)
    else:
        # マッチしなかった場合はNoneを返します。
        return None

class ValidationPipeline:
    def process_item(self, item, spider):
        item['URL'] = extract_username(item['URL'])
        return item

class MongoPipeline(object):
    """
    ItemをMongoDBに保存するPipeline。
    """

    def open_spider(self, spider):
        """
        Spiderの開始時にMongoDBに接続する。
        """
        print(f'{}')
        self.client = MongoClient('localhost', 27017)  # ホストとポートを指定してクライアントを作成。
        self.db = self.client['cricket']  # scraping-book データベースを取得。
        self.collection = self.db['items']  # items コレクションを取得。

    def close_spider(self, spider):
        """
        Spiderの終了時にMongoDBへの接続を切断する。
        """

        self.client.close()

    def process_item(self, item, spider):
        """
        Itemをコレクションに追加する。
        """

        # insert_one()の引数は書き換えられるので、コピーしたdictを渡す。
        self.collection.insert_one(dict(item))
        return item
