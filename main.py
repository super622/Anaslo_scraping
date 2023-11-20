import asyncio
from datetime import datetime

from utils import *

class AnaSloData:
    def get_all_datas(self):
        now = datetime.now()
        # get page data to get region info
        print('==================start===============')
        print(now.strftime("%H:%M:%S"))
        response = send_request('https://ana-slo.com/', 'get', {}, {})
        
        page_data = None
        
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            return {'msg': 'net error', 'data': response}
        
        # get region info from page data
        region_data = get_region_data(page_data)
        print('==================region data===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        # get a list of stores in region
        store_list = get_list_of_stores()
        print('==================store list===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        # get store data by date
        store_data = get_store_data_by_date()
        print('==================get store data by date===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        # get store sub data by date
        store_sub_data = get_store_sub_data_by_date()
        print('==================get store sub data by date===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        # export csv file
        export_csv_file()
        print('==================excel export===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        # save data in database
        save_data_in_database()
        print('==================save data ind database===============')
        now = datetime.now()
        print(now.strftime("%H:%M:%S"))
        
        return {'data': store_sub_data}
        
    def main(self):
        return self.get_all_datas()
    
    # def run(self):
    #     results = asyncio.run(self.main())
    #     return results