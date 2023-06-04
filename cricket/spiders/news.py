import scrapy, re
from time import sleep
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

class NewsSpider(scrapy.Spider):
    name = "news"
    # allowed_domains = ['news.yahoo.co.jp']  # クロール対象とするドメインのリスト。
    # start_urls = ['https://news.yahoo.co.jp/']  # クロールを開始するURLのリスト。
    allowed_domains = ['plaza.rakuten.co.jp']  # クロール対象とするドメインのリスト。
    start_urls = ['https://plaza.rakuten.co.jp/']  # クロールを開始するURLのリスト。

    def __init__(self, search_word, page_limit=10):
        self.search_word = search_word
        self.page_limit = int(page_limit)

    def start_requests(self):
        options = webdriver.ChromeOptions()
        # ヘッドレスモードを有効にするには、次の行のコメントアウトを解除する。
        # options.headless = True

        self.driver = webdriver.Chrome(options = options)
        self.driver.get('https://plaza.rakuten.co.jp/')

        # Search a word
        input_element = self.driver.find_element(By.ID, 'gv')
        # input_element.send_keys('コオロギ*食')
        input_element.send_keys(self.search_word)
        input_element.send_keys(Keys.RETURN)

        # Avoid getting banned
        # sel = Selector(text=self.driver.page_source)
        # forbidden_page_title = sel.xpath('//title/text()').extract_first()
        # if '403' in forbidden_page_title:
        #     self.logger.warn('Access is forbidden. Try again!')
        #     input_search_form2 = self.driver.find_element_by_xpath(
        #         '//input[@name="search_block_form"]')
        #     input_search_form2.send_keys(self.search_word)
        #     input_search_form2.send_keys(Keys.RETURN)

        # Order by Date from Relevance
        selector_element = self.driver.find_element(By.CSS_SELECTOR, 'div.gsc-option-selector')
        #画像のリンクをクリック
        selector_element.click()

        Date_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Date')]")
        #画像のリンクをクリック
        Date_element.click()

        page_num = 1
        while page_num < self.page_limit+1:
            try:
                # Get articles
                sel = Selector(text=self.driver.page_source)
                article_urls = sel.css('a.gs-title::attr(href)').getall()

                for article_url in article_urls[1::2]:
                    yield Request(url=article_url, callback=self.parse_article)

                    # 記事のURLからプロフィールのURLへアクセスする
                    profile_url = re.sub(pattern = "/diary.*", repl = "/profile", string = article_url)
                    yield Request(url=profile_url, callback=self.parse_profile)

                # Proceed a next page
                page_num = page_num + 1

                if page_num > self.page_limit:
                    break

                next_page_element = self.driver.find_element(By.CSS_SELECTOR, f'[aria-label="ページ {page_num}"]')
                # 次のページへのリンクをクリック
                next_page_element.click()

                # next_page = self.driver.find_element_by_xpath(
                #     '//li[contains(@class, "pager-next")]/a')
                # next_page.click()
                sleep(3)

            except NoSuchElementException:
                self.driver.quit()
                break
        else:
            self.driver.quit()

    def parse_article(self, response):
        """
        トップページのトピックス一覧から個々のトピックスへのリンクを抜き出して表示する。
        """
        linked_information = response.xpath('//a/@href').extract()
        body = response.css('span::text').extract()
        yield {'linked_information': linked_information, 'article_body': body}

    def parse_profile(self, response):
        """
        トップページのトピックス一覧から個々のトピックスへのリンクを抜き出して表示する。
        """
        nickname = response.css('p#pfofileNickname::text').extract()
        description = response.css('p#pfofileDescription::text').extract()
        yield {'nickname': nickname, 'description': description}
