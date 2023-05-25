import re
from urllib.parse import urlparse
from scrapy_playwright.page import PageMethod

async def errback(failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

def meta_scrapy_request():
        return dict(
        download_timeout=60,
        playwright = True,
        playwright_include_page = True,
        playwright_page_methods = [
            PageMethod('wait_for_selector','img'),
            PageMethod('wait_for_timeout',60000),
            #PageMethod('set_default_navigation_timeout',60000)
            ],
        errback = errback,
        dont_filter = True #filter duplicate requests
        )

def urlGenerate(url, response, prevent_url=False):
    parsed_uri = urlparse(response.url)
    if url.startswith('http://') or url.startswith('https://'):
        return url
    elif url.startswith('/'):
        if prevent_url and url.startswith('//'):
            return url.replace('//','')
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)+url
    else: 
        url = url.replace('//','/')
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)+url
    
def formatPrice(price):
    return re.sub('[^0-9]+', '', str(price))#A-Za-z0-9
