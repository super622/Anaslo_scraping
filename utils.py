import requests

from bs4 import BeautifulSoup

store_list_data = []
region_list_data = []

# send request
def send_request(url, request_type, header, param):
    headers = {
        'Content-Type': 'application/json',
        "Accept": "application/json",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    }
    
    response = None
    if request_type == 'get':
        response = requests.get(url, params=param, headers=headers)
    else:
        response = requests.post(url, params=param, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        return ''
    
# convert html to element format
def parse_html_to_element(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# get region data from page data
def get_region_data(page_data):
    parent_elements = page_data.find_all('div', {'class': 'pref_list'})
    parent_element = parent_elements[1]
    region_data = []
    child_elements = parent_element.find_all('a')
    
    for element in child_elements:
        data = {
            'url': element['href'],
            'name': element.text
        }
        region_data.append(data)
    global region_list_data
    region_list_data = region_data
    return region_data

# get a list of stores from region data
def get_list_of_stores():
    global region_list_data
    region_data = region_list_data
    all_store_data = []
    
    for region in region_data:
        response = send_request(region['url'], 'get', {}, {})
        page_data = None
        
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            return store_data
        
        table_data = page_data.find('div', {'class': 'hall-list-table'})
        table_body = table_data.find('div', {'class': 'table-body'})
        table_rows = table_body.find_all('div', {'class': 'table-row'})
        
        sub_store_data = []
        for element in table_rows:
            table_data = element.find_all('div', {'class': 'table-data-cell'})
            data = {
                'url': table_data[0].find('a')['href'],
                'name': table_data[0].text,
                'city': table_data[1].text,
                'data': []
            }
            sub_store_data.append(data)
        
        all_store_data.append({'region': region['name'], 'stores': sub_store_data})
        global store_list_data
        store_list_data = all_store_data
    
    return all_store_data

# get store data
def get_store_data():
    global store_list_data
    store_list = store_list_data
    
    for stores in store_list:
        for store in stores['stores']:
            response = send_request(store['url'], 'get', {}, {})
        
            page_data = None
            
            if response != '':
                page_data = parse_html_to_element(response)
            else:
                continue
            
            store_data = []
            table_data = page_data.find_all('div', {'class': 'table-row'})
            
            for i in range(len(table_data)):
                if i == 0:
                    continue
                table_cell_data = table_data[i].find_all('div', {'class': 'table-data-cell'})
                return table_cell_data[0]
                data = {
                    # 'url': table_cell_data[0].find('a')['href'],
                    'total_diff': table_cell_data[1].text,
                    'avg_diff': table_cell_data[2].text,
                    'avg_g_num': table_cell_data[3].text,
                    'win_rate': table_cell_data[4].text
                }
                store_data.append(data)
            
            store['data'] = store_data
    
    store_list_data = store_list
    return store_list_data