import scrapy
import pycountry
import json
from locations.items import GeojsonPointItem
from locations.categories import Code
import uuid

class StoreLocatorSpider(scrapy.Spider):
    name = 'steimatzky_isr_dac'
    start_urls = ['https://www.steimatzky.co.il/storelocator']

    def parse(self, response):
        store_name_list = []
        store_address_list = []
        activity_time_list = []
        phone_number_list = []

        storename = response.css('div.store_title')
        for strname in storename:
            storenametext = strname.css('::text').get().strip()
            store_name_list.append(storenametext)

        address_div_elements = response.css('div.store_address')
        for add in address_div_elements:
            street_span = add.css('span.street::text').get()
            city_span = add.css('span.city::text').get()
            address = street_span.strip() + city_span.strip()
            store_address_list.append(address)

        open_hours_divs = response.css('div.open_hours')
        for div in open_hours_divs:
            p_tags = div.css('p::text').getall()
            hours = [p.strip() for p in p_tags]
            activity_time_list.append(hours)

        phonenumber_a = response.css('a.store_telephone')
        for numbers in phonenumber_a:
            phnumber = numbers.css('span::text').getall()
            phone_number_list.append(''.join(phnumber).strip())

        li_items = response.css('ul.stores li')
        for i, li in enumerate(li_items):
            latitude = li.attrib['data-latitude']
            longitude = li.attrib['data-longitude']
            
            data = {
                'ref': uuid.uuid4().hex,
                'name': store_name_list[i],
                'addr_full': store_address_list[i],
                'opening_hours': activity_time_list[i],
                'phone': phone_number_list[i],
                'lat': latitude,
                'lon': longitude,
                'chain_id':"9163",
                'chain_name':"Steimatzky",
                "brand":"Steimatzky",
                "website":"https://www.steimatzky.co.il/storelocator",
            }
            yield GeojsonPointItem(**data)
