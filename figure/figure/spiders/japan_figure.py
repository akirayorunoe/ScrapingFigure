from datetime import datetime
import hashlib
import scrapy
from figure.helpers import urlGenerate, meta_scrapy_request,formatPrice
from figure.items import FigureItem
from scrapy_redis.spiders import RedisSpider

class JapanFigureSpider(scrapy.Spider):
    name = "japan_figure"
    allowed_domains = ['japanfigure.vn','product.hstatic.net']
    custom_settings = {#setting cho spider nhất định và ghi đè lên setting project
        'DOWNLOAD_DELAY': 2.5,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {#remove timeout
            "timeout": 0,
        },
        'ROTATING_PROXY_LIST': []#không dùng proxy
    }
    
    def start_requests(self):
        # List of URLs to scrape
        url='https://japanfigure.vn/collections/all?page=1'
        yield scrapy.Request(url, meta=meta_scrapy_request())
        
    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        for figure in response.xpath('//div[@class="col-md-3 col-sm-4 col-xs-6 product-loop"]/div'):
            url = urlGenerate(figure.xpath('./div[@class="proloop-image "]/a/@href').get(),response)
            yield scrapy.Request(url,
                callback=self.parse_detail_product,
                meta= meta_scrapy_request()
                )
        #Pagination
        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            nextPageUrl = urlGenerate(next_page,response)
            yield scrapy.Request(nextPageUrl, meta=meta_scrapy_request())

    async def parse_detail_product(self, response):
        page = response.meta["playwright_page"]
        item = FigureItem()
        item['url'] = response.url
        item['name'] = response.xpath('//*[@id="detail-product"]/div/div[1]/div[2]/h1/text()').get()#dấu chấm đầu tiên để chỉ định rằng bạn muốn tìm phần tử con của phần tử đang được xử lý bởi vòng lặp for
        item['images']=[]
        for imgList in response.xpath('/html/body/div[1]/main/div/section[1]/div/div/div[1]/div/div/div[2]/ul/div/div/li'):
            img=imgList.xpath('./a/@href').get()
            img=urlGenerate(img,response,True)
            item['images'].append(img)
        price = response.xpath('//*[@id="price-preview"]/span/text()').get()
        item['price'] = formatPrice(price)#nếu không dùng text() sẽ in ra cả selector cuối cùng
        
        # Compute hash of the item
        m = hashlib.sha256()
        m.update(item["url"].encode('utf-8'))
        m.update(str(item["price"]).encode('utf-8'))
        m.update(str(item["images"]).encode('utf-8'))
        m.update(item["name"].encode('utf-8'))
        item_hash = m.hexdigest()
        item["hash"] = item_hash

        item['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await page.close()#Close page after finish scraping
        yield item

# from datetime import datetime
# import hashlib
# import scrapy
# from figure.helpers import urlGenerate, meta_scrapy_request,formatPrice
# from figure.items import FigureItem
# from scrapy_redis.spiders import RedisSpider
# from scrapy.shell import inspect_response

# class JapanFigureSpider(RedisSpider):
#     name = "japan_figure"
#     allowed_domains = ['japanfigure.vn','product.hstatic.net']
#     custom_settings = {#setting cho spider nhất định và ghi đè lên setting project
#         'DOWNLOAD_DELAY': 2.5,
#         "PLAYWRIGHT_LAUNCH_OPTIONS": {#remove timeout
#             "timeout": 0,
#         },
#         'ROTATING_PROXY_LIST': []#không dùng proxy
#     }
#     redis_key = "japan_figure:start_urls"
#     redis_batch_size = 2 # Số lượng URL tối đa được trích xuất từ hàng đợi Redis mỗi lần
#      # Max idle time(in seconds) before the spider stops checking redis and shuts down
#     max_idle_time = 7
    
#     def make_requests_from_url(self, url):
#         return scrapy.Request(url, meta=meta_scrapy_request())
    
#     async def parse(self, response):
#         page = response.meta.get("playwright_page")
#         if page:
#             await page.close()
#         for figure in response.xpath('//div[@class="col-md-3 col-sm-4 col-xs-6 product-loop"]/div'):
#             url = urlGenerate(figure.xpath('./div[@class="proloop-image "]/a/@href').get(),response)
#             yield scrapy.Request(url,
#                 callback=self.parse_detail_product,
#                 meta= meta_scrapy_request()
#                 )
#         #Pagination
#         # next_page = response.xpath('//a[@class="next"]/@href').get()
#         # if next_page:
#         #     nextPageUrl = urlGenerate(next_page,response)
#         #     yield scrapy.Request(nextPageUrl, meta=meta_scrapy_request())
    
#     async def parse_detail_product(self, response):
#         page = response.meta.get("playwright_page")
#         item = FigureItem()
#         item['url'] = response.url
#         item['name'] = response.xpath('//*[@id="detail-product"]/div/div[1]/div[2]/h1/text()').get()#dấu chấm đầu tiên để chỉ định rằng bạn muốn tìm phần tử con của phần tử đang được xử lý bởi vòng lặp for
#         item['images']=[]
#         for imgList in response.xpath('/html/body/div[1]/main/div/section[1]/div/div/div[1]/div/div/div[2]/ul/div/div/li'):
#             img=imgList.xpath('./a/@href').get()
#             img=urlGenerate(img,response,True)
#             item['images'].append(img)
#         price = response.xpath('//*[@id="price-preview"]/span[@class="pro-price"]/text()').get()
#         item['price'] = formatPrice(price)#nếu không dùng text() sẽ in ra cả selector cuối cùng
        
#         # Compute hash of the item
#         m = hashlib.sha256()
#         m.update(item["url"].encode('utf-8'))
#         m.update(str(item["price"]).encode('utf-8'))
#         m.update(str(item["images"]).encode('utf-8'))
#         m.update(item["name"].encode('utf-8'))
#         item_hash = m.hexdigest()
#         item["hash"] = item_hash

#         item['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         if page:
#             await page.close()
#         yield item



