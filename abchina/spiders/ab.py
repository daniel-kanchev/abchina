import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from abchina.items import Article


class AbSpider(scrapy.Spider):
    name = 'ab'
    start_urls = ['http://www.uk.abchina.com/en/news/']

    def parse(self, response):
        articles = response.xpath('//ul[@class="right-news-hr"]/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%Y-%m-%d')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="right-news right-news-det"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
