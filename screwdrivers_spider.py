import scrapy
from scrapy.crawler import CrawlerProcess


class GetAllProductsUrlsSpider(scrapy.Spider):
    name = "allProductsUrls"
    base_url = 'https://mr-bricolage.bg'

    start_urls = [
        'https://mr-bricolage.bg/instrumenti/elektroprenosimi-instrumenti/vintoverti/c/006003013?q=%3Arelevance&page=0&priceValue=',
        'https://mr-bricolage.bg/instrumenti/elektroprenosimi-instrumenti/vintoverti/c/006003013?q=%3Arelevance&page=1&priceValue=',
        'https://mr-bricolage.bg/instrumenti/elektroprenosimi-instrumenti/vintoverti/c/006003013?q=%3Arelevance&page=2&priceValue=',
        'https://mr-bricolage.bg/instrumenti/elektroprenosimi-instrumenti/vintoverti/c/006003013?q=%3Arelevance&page=3&priceValue=',
    ]

    def parse(self, response):
        urls = []
        for prod in response.css('div.product'):
            cur_url = self.base_url + prod.css('div.image div.actions a.add-to-search::attr(href)').get()
            urls.append(cur_url)
        f = open("../../ProductsUrls.csv", "a")
        print(urls)
        for el in urls:
            f.write(el + '\n')
        f.close()


class AllProductsDetailsSpider(scrapy.Spider):
    name = "screwdriversInfo"
    f = open("../../ProductsUrls.csv", "r")
    urls = f.readlines()
    f.close()

    start_urls = urls

    def parse(self, response):
        for prod_details in response.css('body.page-productDetails'):
            product_name = prod_details.css(
                'section.product-single div.container div.row div.col-md-6 div.row:first-child'
                ' div.col-md-6 h1::text').get()

            product_price = prod_details.css(
                'section.product-single div.container div.row div.col-md-6 div.row:last-child'
                ' div p::attr(data-price-value)').get()

            product_pictures = prod_details.css(
                'section.product-single div.container div.row div.col-md-6 div.owl-thumbs'
                ' div.owl-thumb-item img::attr(src)').getall()

            characteristics_list = (list(map(lambda x: x.replace("\xa0", ""), prod_details.css(
                'section.product-details div.container div.row div.col-md-12 div.product-classifications table'
                ' tbody tr td').xpath('normalize-space()').getall())))

            keys = [v for i, v in enumerate(characteristics_list) if i % 2 == 0]
            values = [v for i, v in enumerate(characteristics_list) if i % 2 != 0]
            characteristics = dict(zip(keys, values))

            if characteristics:
                if characteristics['Марка']:
                    product_name += ' ' + characteristics['Марка']

            cur_product = {'product_name': product_name,
                           'product_price': product_price,
                           'product_picture': product_pictures,
                           'characteristics': characteristics,
                           }

            product_keys_str = ['product_name', 'product_price', 'product_picture', 'characteristics']

            f = open("../../AllProductsData.json", "a")
            for key in product_keys_str:
                if key in ['product_name', 'product_price']:
                    f.write(cur_product[key] + ' ')
                elif key == 'product_picture':
                    if len(cur_product[key]) != 0:
                        for index in range(len(cur_product[key])):
                            f.write(f'({cur_product[key][index]})' + ' ')
                elif key == 'characteristics':
                    if characteristics:
                        for key_inner in keys:
                            f.write(key_inner + ': ' + cur_product[key][key_inner] + ';    ')
                    else:
                        f.write('No available characteristics for this product')
                    f.write('\n')
                f.write('\n')
            f.close()


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(GetAllProductsUrlsSpider)
process.crawl(AllProductsDetailsSpider)
process.start()
