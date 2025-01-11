import scrapy
import json
import re
from locations.items import GeojsonPointItem

class osesSpider(scrapy.Spider):
    name = "oses_tur_dac"
    start_urls = ["https://www.oses.com.tr/oses-cigkofte-subeleri"]
    
    def parse(self, response):
        script_tags = response.xpath('//script[@type="text/javascript"]')

        for script_tag in script_tags:
            script_string = script_tag.get()
            if script_string and 'gMaps.locations' in script_string:
                start_index = script_string.index('[')
                end_index = script_string.index(']', start_index) + 1
                data_string = script_string[start_index:end_index]
                data = json.loads(data_string)
                for location in data:
                    opening_hours = None
                    if location['infowindow']:
                        # extract the opening hours from the infowindow field
                        match = re.search(r'<span>(.*?)</span>', location['infowindow'])
                        if match:
                            opening_hours = match.group(1).strip()

                    date= {
                        "ref":location['index'],
                        'name':location['name'],
                        'lat' : location['lat'],
                        'lon' : location['lng'],
                        'city':location['cityName'],
                        'phone':location['phone'],
                        'opening_hours': opening_hours,
                        'chain_id':"24109",
                        'chain_name':"Oses Çigköfte",
                        "brand":"Oses Çigköfte",
                        "website":"https://www.oses.com.tr/oses-cigkofte-subeleri",
                    }
                    yield GeojsonPointItem(**date)
