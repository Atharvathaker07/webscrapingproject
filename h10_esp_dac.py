import scrapy
import json
import uuid
from locations.items import GeojsonPointItem
from locations.categories import Code

class HotelSpider(scrapy.Spider):
    name = 'h10_esp_dac'
    start_urls = ['https://cmspro.h10hotels.com/_vti_bin/H10_WebServices/H10_Login.svc/GetDestinosFooter/1033?_=1686247491136']

    def parse(self, response):
        json_data = json.loads(response.text)

        city_links_list = []
        count = 0
        for destination_group in json_data:
            for destination in destination_group:
                name = destination['Name']
                url_destino = destination['UrlDestino']
                city_links_list.append(url_destino)
                count += 1
                if count >= 21:
                    break
            if count >= 21:
                break

        hotel_links_list = set()

        for city_link in city_links_list:
            yield scrapy.Request(city_link, callback=self.parse_hotel_links)

    def parse_hotel_links(self, response):
        a_tags = response.css('div.span3 a')
        for a in a_tags[:-1]:
            links = a.attrib['href']
            yield scrapy.Request(links, callback=self.parse_hotel_details)

    def parse_hotel_details(self, response):
        address_element = response.css('.address #streetAddress')
        address = address_element.css('::text').get().strip()
        telephone_element = response.css('span#telephone')
        telephone_number = telephone_element.css('::text').get().strip()
        email_tag = response.css('div.address a')
        email_address = email_tag.css('::text').get()
        coordinates = response.css('#hdfLongitudLatitud::attr(value)').get()

        # Split the coordinates into latitude and longitude
        if coordinates:
            latitude, longitude = map(float, coordinates.strip().split(','))
        else:
            latitude = None
            longitude = None

        data = {
            'ref': uuid.uuid4().hex,
            'name': response.url.split('/')[-1].replace('-', ' '),
            'addr_full': address,
            'phone': telephone_number,
            'email': email_address,
            'lat': latitude,
            'lon': longitude,
            'chain_id':"2098",
            'chain_name':"H10",
            "brand":"H10",
            "website":"https://www.h10hotels.com/en",
        }
        yield GeojsonPointItem(**data)
