from datetime import datetime
import hashlib
import scrapy
from figure.items import FigureItem
from scrapy.shell import inspect_response

from figure.helpers import meta_scrapy_request, urlGenerate,formatPrice


class BucketAndShovelSpider(scrapy.Spider):
    name = "bucket_and_shovel"
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
    allowed_domains = ['bucketandshovel.com','cdn.shopify.com']

    custom_settings = {#setting cho spider nhất định và ghi đè lên setting project
        'DOWNLOAD_DELAY': 2,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {#remove timeout
            "timeout": 0,
        }
    }

    def start_requests(self):
        url = 'https://bucketandshovel.com/collections/best-selling?page=1'
        yield scrapy.Request(url, meta=meta_scrapy_request())

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        for figure in response.xpath('//*[@id="Collection"]/ul[1]/li'):
            url = urlGenerate(figure.xpath('./div/a/@href').get(),response)
            yield scrapy.Request(url,
                callback=self.parse_detail_product,
                meta= meta_scrapy_request()
                )
        #Pagination
        next_page = response.xpath('//*[@id="Collection"]/ul[2]/li[3]/a/@href').get()
        if next_page:
            nextPageUrl = urlGenerate(next_page,response)
            yield scrapy.Request(nextPageUrl, meta=meta_scrapy_request())

            
    async def parse_detail_product(self, response):
        page = response.meta["playwright_page"]
        page.set_default_timeout(timeout=120000)
        item = FigureItem()
        item['url'] = response.url
        item['name'] = response.xpath('//*[contains(@id, "ProductSection-template--") and contains(@id, "__template")]/div/div[2]/h1/text()').get()
        item['images']=[]
        for imgList in response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]/div/div[1]/div[2]/div/div/div'):
            img=imgList.xpath('.//img/@src').get()
            img=urlGenerate(img,response,True)
            item['images'].append(img)
        #if item['images'] still empty
        if not item['images']:
            item['images'].append(response.xpath('//*[contains(@id,"product-featured-image-")]/@src').get())
        # if response.url == 'https://bucketandshovel.com/products/pre-order-coolbear-studio-elden-ring-malenia-blade-of-miquella':
        #     inspect_response(response, self)
        #Sale price
        #//*[@id="ProductSection-template--15307827413172__template"]/div/div[2]/div[1]/div/span/span
        price = response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]//*[@class="product-price on-sale"]/span[@class="money"]/text()').get()
        #price = response.xpath('//div[@class="product-block mobile-only product-block--sales-point"]//span[@class="product-price on-sale"]/text()').get()
        if price == None:
            #Regular price
            price = response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]//*[@class="product-price"]/span[@class="money"]/text()').get()
        #compare price
        #price = response.xpath('//div[@class="product-block mobile-only product-block--sales-point"]//s[@class="product-compare-price"]/text()').get()
        item['price'] = formatPrice(price)

        # Compute hash of the item
        m = hashlib.sha256()
        m.update(item["url"].encode('utf-8'))
        m.update(str(item["price"]).encode('utf-8'))
        m.update(str(item["images"]).encode('utf-8'))
        m.update(item["name"].encode('utf-8'))
        item_hash = m.hexdigest()
        item["hash"] = item_hash

        item['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await page.close()
        #Check if price, name are null and image is empty
        if not (item['price'] and item['name'] and item['images']):
            inspect_response(response, self)
        yield item
    
# from datetime import datetime
# import hashlib
# import scrapy
# from figure.items import FigureItem
# from scrapy.shell import inspect_response
# from scrapy_redis.spiders import RedisSpider

# from figure.helpers import meta_scrapy_request, urlGenerate,formatPrice


# class BucketAndShovelSpider(RedisSpider):
#     name = "bucket_and_shovel"
#     # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
#     allowed_domains = ['bucketandshovel.com','cdn.shopify.com']

#     custom_settings = {#setting cho spider nhất định và ghi đè lên setting project
#         'DOWNLOAD_DELAY': 2.5,
#         "PLAYWRIGHT_LAUNCH_OPTIONS": {#remove timeout
#             "timeout": 0,
#         },
#         #'ROTATING_PROXY_LIST': []#không dùng proxy
#     }

#     redis_key = "bucket_and_shovel:start_urls"
#     redis_batch_size = 2 # Số lượng URL tối đa được trích xuất từ hàng đợi Redis mỗi lần
#      # Max idle time(in seconds) before the spider stops checking redis and shuts down
#     max_idle_time = 7

#     def make_requests_from_url(self, url):
#         return scrapy.Request(url, meta=meta_scrapy_request())

#     async def parse(self, response):
#         page = response.meta.get("playwright_page")
#         if page:
#             await page.close()
#         for figure in response.xpath('//*[@id="Collection"]/ul[1]/li'):
#             url = urlGenerate(figure.xpath('./div/a/@href').get(),response)
#             yield scrapy.Request(url,
#                 callback=self.parse_detail_product,
#                 meta= meta_scrapy_request()
#                 )
#         #Pagination
#         # next_page = response.xpath('//*[@id="Collection"]/ul[2]/li[3]/a/@href').get()
#         # if next_page:
#         #     nextPageUrl = urlGenerate(next_page,response)
#         #     yield scrapy.Request(nextPageUrl, meta=meta_scrapy_request())

            
#     async def parse_detail_product(self, response):
#         page = response.meta.get("playwright_page")
#         item = FigureItem()
#         item['url'] = response.url
#         item['name'] = response.xpath('//*[contains(@id, "ProductSection-template--") and contains(@id, "__template")]/div/div[2]/h1/text()').get()
#         item['images']=[]
#         for imgList in response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]/div/div[1]/div[2]/div/div/div'):
#             img=imgList.xpath('.//img/@src').get()
#             img=urlGenerate(img,response,True)
#             item['images'].append(img)
#         #if item['images'] still empty
#         if not item['images']:
#             item['images'].append = response.xpath('//*[contains(@id,"product-featured-image-")]/@src').get()
#         # if response.url == 'https://bucketandshovel.com/products/pre-order-coolbear-studio-elden-ring-malenia-blade-of-miquella':
#         #     inspect_response(response, self)
#         #Sale price
#         #//*[@id="ProductSection-template--15307827413172__template"]/div/div[2]/div[1]/div/span/span
#         price = response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]//span[@class="product-price on-sale"]/text()').get()
#         #price = response.xpath('//div[@class="product-block mobile-only product-block--sales-point"]//span[@class="product-price on-sale"]/text()').get()
#         if price == None:
#             #Regular price
#             price = response.xpath('//*[contains(@id,"ProductSection-template--") and contains(@id,"__template")]//span[@class="product-price"]/text()').get()
#         #compare price
#         #price = response.xpath('//div[@class="product-block mobile-only product-block--sales-point"]//s[@class="product-compare-price"]/text()').get()
#         item['price'] = formatPrice(price)

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
#         #Check if price, name are null and image is empty
#         if not (item['price'] and item['name'] and item['images']):
#             inspect_response(response, self)
#         yield item
