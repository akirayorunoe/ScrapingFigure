
from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from figure.spiders.japan_figure import JapanFigureSpider
from figure.spiders.bucket_and_shovel import BucketAndShovelSpider

def main():
    settings = Settings()
    settings.setmodule("figure.settings") # Thay thế bằng đường dẫn đến settings của project
    settings.update(BucketAndShovelSpider.custom_settings)
    #settings.update(JapanFigureSpider.custom_settings)

    process = CrawlerProcess(settings=settings)
    process.crawl(BucketAndShovelSpider)
    #process.crawl(JapanFigureSpider)
    process.start()

if __name__ == "__main__":
    main()
