from dataclasses import Field, field
import scrapy
from scrapy import Item
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class DistrictSpider(scrapy.Spider):
    name = 'districts'

    def __init__(self):
        self.start_urls = ['http://www.kreisnavigator.de/kreisnavigator/frmalps.htm']

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.driver.implicitly_wait(2)

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.switch_to.frame("brdalphs")
        items = self.extract_items()
        self.driver.close()
        return items

    def extract_items(self):
        extracted_districts_a = self.driver.find_elements_by_xpath('//table/tbody//a')

        items = []
        for extracted_district_a in extracted_districts_a:
            item = self.DistrictItem()
            item['url'] = extracted_district_a.get_attribute('href')
            item['name'] = extracted_district_a.get_attribute('text')
            items.append(item)

        return items

    class DistrictItem(Item):
        url = scrapy.Field()
        name = scrapy.Field()
