from bs4 import BeautifulSoup
import scrapy
import re
import uuid
from locations.items import GeojsonPointItem

class KofteSpider(scrapy.Spider):
    name = 'cigkoftecisaitusta_tur_dac'
    start_urls = ['https://menuburada.com/araclar/restoran-zincirleri/cig-kofteci-sait-usta-subeleri']

    def parse(self, response):
        all_links_list = []
        city_locat_link = []

        # to pick citylinks from the class gselect sifisrsol f20 and put them in all_linkss_list
        select_elem = response.xpath('//select[contains(@class,"gselect sifirsol f20 pson ayukari1")]')
        if select_elem:
            options = select_elem.xpath('.//option')
            for option in options:
                all_links_list.append(option.attrib['value'])

        imp_links_list = all_links_list[1:]

        for link1 in imp_links_list:
            yield scrapy.Request(link1, callback=self.parse_city_links)

    def parse_city_links(self, response):
        city_locat_link = []

        # finding storelinks present inside main citylink
        for blockquote in response.xpath('//blockquote'):
            link = blockquote.xpath('.//a/@href').get()
            actual_links = f"https://menuburada.com/{link}"
            city_locat_link.append(actual_links)

        for link2 in city_locat_link:
            yield scrapy.Request(link2, callback=self.parse_store_details)

    def parse_store_details(self, response):
        link_soup2 = BeautifulSoup(response.text, 'lxml')
        storename = link_soup2.select_one('.mh1').text.strip()
        storename_list = [storename] if storename else []

        mekansutun1_snippet = link_soup2.select_one('.mekansutun1').text.strip()
        phone_number_pattern = r'\d{1}\(\d{3}\) \d{3} \d{2} \d{2}'
        phone_number_match = re.search(phone_number_pattern, mekansutun1_snippet)
        if phone_number_match:
            phone_number = phone_number_match.group(0)
            phone_list = [phone_number]
        else:
            phone_list = ["Phone number not found."]

        mekansutun1_add = link_soup2.select('.mekansutun1 p')
        address = mekansutun1_add[2].text.strip() if len(mekansutun1_add) > 2 else None
        final_address = address.replace('  ', '').replace('\r', '').replace('\n', ' ') if address else None
        address_list = [final_address] if final_address else []

        mekansutun2_elem = link_soup2.select_one('.mekansutun2')
        if mekansutun2_elem:
            working_hours_list = []
            for elem in mekansutun2_elem.children:
                if elem.name != 'h2' and (elem.name != 'p' or 'pilk' not in elem.get('class', [])):
                    text = elem.text.strip()
                    if text:
                        working_hours_list.append(text)
        else:
            working_hours_list = ["Working hours not found."]


        coord_tag = response.xpath('//a[contains(@href, "maps?q=")]')
        if coord_tag:
            coords = coord_tag.xpath('./text()').get().strip()
            lat, lng = map(float, coords.split(","))
            latitude = lat
            longitude = lng
            

        data= {
            'ref':uuid.uuid4().hex,
            'name': storename,
            'phone': phone_number,
            'opening_hours': working_hours_list,
            'addr_full': final_address,
            'lat': latitude,
            'lon':longitude,
            'chain_id':"7751",
            'chain_name':"Cigkofteci Sait Usta",
            "brand":"Cigkofteci Sait Usta",
            "website":"https://menuburada.com/araclar/restoran-zincirleri/cig-kofteci-sait-usta-subeleri"

        }

        yield GeojsonPointItem(**data)