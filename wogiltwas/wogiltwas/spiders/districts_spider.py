from dataclasses import Field, field
import scrapy
from scrapy import Item
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class DistrictSpider(scrapy.Spider):
    name = 'districts'

    def __init__(self):
        self.start_urls = ['http://www.kreisnavigator.de/kreisnavigator/frmalps.htm']

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.driverDistricts = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.driverResults = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.switch_to.frame("brdalphs")
        items = self.extract_district_items()
        self.driver.close()
        for item in items:
            self.log('Current Website: ' + item.get('url'));
            item = self.extract_url_items(item)
        logfile = open("logfile.txt", "a")
        logfile.write(str(items))
        logfile.close()

    def extract_district_items(self):
        extracted_districts_a = self.driver.find_elements_by_xpath('//table/tbody//a')

        items = []
        for extracted_district_a in extracted_districts_a:
            item = self.DistrictItem()
            item['url'] = extracted_district_a.get_attribute('href')
            item['name'] = extracted_district_a.get_attribute('text')
            items.append(item)

        return items

    def extract_url_items(self, item):
        self.driverDistricts.get(item.get('url'))

        # TODO include landing page analytics
        # self.analyse_results(item, item.get('url'))

        item['suburls'] = self.driverDistricts.find_elements_by_xpath('//body//a[contains(@href,"corona")]')

        for suburl in item['suburls']:
            item = self.analyse_results(item, suburl.get_attribute('href'))
            if item.get('pdflink') != '':
                break

            # backup code
            # suburlnodes = suburl.find_elements_by_xpath("/descendant::*")
            # for suburlnode in suburlnodes:
            #     if suburlnode.text.find("Corona") != -1:
            #         self.log(suburlnode.text)
            #         self.log(suburl.get_attribute('href'))
            #         break
        self.driverDistricts.close()

        return item

    def analyse_results(self, item, url):
        self.driverResults.get(url)
        pdfitems = self.driverResults.find_elements_by_xpath('//a[contains(@href, ".pdf")]')
        item['pdflinks'] = []
        for pdfitem in pdfitems:
            item['pdflinks'].append(pdfitem.get_attribute("href"))

        self.driverResults.close()

        return item

    class DistrictItem(Item):
        url = scrapy.Field()
        name = scrapy.Field()
        suburls = scrapy.Field()
        pdflinks = scrapy.Field()
