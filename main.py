import asyncio

from utils import *

class AnaSloData:
    def get_all_datas(self):
        # get page data to get region info
        response = send_request('https://ana-slo.com/', 'get', {}, {})
        
        page_data = None
        
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            return {'msg': 'net error', 'data': response}
        
        # get region info from page data
        region_data = get_region_data(page_data)
        
        # get a list of stores in region
        store_list = get_list_of_stores()
        
        # get a store data 
        store_data = get_store_data()
        
        return {'data': store_data}
        
    def main(self):
        return self.get_all_datas()
    
    # def run(self):
    #     results = asyncio.run(self.main())
    #     return results