import scrapy
from bookspider.items import BookspiderItem
from bs4 import BeautifulSoup


class BookspiderSpider(scrapy.Spider):
    name = "BookSpider"
    allowed_domains = ["bqgui.cc"]
    start_urls = ["https://www.bqgui.cc/book/1510/1.html"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        try:
            html = response.body.decode('utf-8')
        except UnicodeDecodeError:
            html = response.body.decode('gbk', errors='ignore')

        soup = BeautifulSoup(html, 'html.parser')

        # 提取章节标题
        title = soup.select_one('h1.wap_none').get_text()

        # 提取章节内容
        content = [p.get_text() for p in soup.select('#chaptercontent')]

        # 清理内容中的特殊字符和不必要的空白
        cleaned_content = ' '.join(content).replace('\u3000', '').strip()

        # 移除不需要的部分,这个是每一页都有的重复的不必要的内容，可以直接删除掉
        cleaned_content = cleaned_content.replace(
            '请收藏本站：https://www.bqgui.cc。笔趣阁手机版：https://m.bqgui.cc',
            ''
        ).replace('『点此报错』『加入书签』', '').strip()

        item = BookspiderItem()
        item['title'] = title
        item['content'] = cleaned_content

        yield item

        # Extract next page link and follow
        current_page = int(response.url.split('/')[-1].split('.')[0])
        next_page = current_page + 1
        next_page_link = f"https://www.bqgui.cc/book/1510/{next_page}.html"
        self.log(f'Following next page link: {next_page_link}')
        yield response.follow(next_page_link, self.parse)
