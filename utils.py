import requests
import xlwt
import pathlib
import mysql.connector

import conf

from mysql.connector import errorcode
from bs4 import BeautifulSoup

total_data = []
region_list_data = []
store_list_data = []
store_data_by_date = []
store_sub_data = []

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
    
    for i in range(len(child_elements)):
        data = [(i + 1), child_elements[i]['href'], child_elements[i].text]
        region_data.append(data)
    
    global region_list_data
    region_list_data = region_data
    return region_data

# get a list of stores from region data
def get_list_of_stores():
    global region_list_data
    region_data = region_list_data
    all_store_list = []
    cnt = 0
    
    for region in region_data:
        response = send_request(region[1], 'get', {}, {})
        page_data = None
        
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            return all_store_list
        
        table_data = page_data.find('div', {'class': 'hall-list-table'})
        table_body = table_data.find('div', {'class': 'table-body'})
        table_rows = table_body.find_all('div', {'class': 'table-row'})
        
        i = 0
        for i in range(len(table_rows)):
            table_data = table_rows[i].find_all('div', {'class': 'table-data-cell'})
            data = [(cnt + i), region[0], table_data[0].find('a')['href'], table_data[0].text, table_data[1].text]
            all_store_list.append(data)
        print(f"store list i => {i} = {len(table_rows)}")
        cnt += (i + 1)
        # test
        global store_list_data
        store_list_data = all_store_list
        return all_store_list

# get store data by date
def get_store_data_by_date():
    global store_list_data
    store_list = store_list_data
    
    cnt = 0
    store_data = []
    for store in store_list:
        response = send_request(store[2], 'get', {}, {})
    
        page_data = None
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            continue
            
        table_data = page_data.find_all('div', {'class': 'table-row'})
        i = 0
        for i in range(len(table_data)):
            if i == 0:
                continue
            
            table_cell_data = table_data[i].find_all('div', {'class': 'table-data-cell'})
            if table_cell_data[0].find('a') != None:
                data = [
                    (cnt + i), 
                    store[0], 
                    table_cell_data[0].find('a')['href'],
                    table_cell_data[0].text,
                    table_cell_data[1].text,
                    table_cell_data[2].text,
                    table_cell_data[3].text,
                    table_cell_data[4].text
                ]
                store_data.append(data)
            else:
                break
        cnt += (i + 1)
    global store_data_by_date
    store_data_by_date = store_data
    return store_data_by_date

# get sub data from data by date
def get_store_sub_data_by_date():
    global store_data_by_date
    temp_store_data_by_date = store_data_by_date
    
    cnt = 0
    sub_data = []
    for store_data in temp_store_data_by_date:
        response = send_request(store_data[2], 'get', {}, {})

        page_data = None
        if response != '':
            page_data = parse_html_to_element(response)
        else:
            continue
        
        table = page_data.find('table', {'id': 'all_data_table'})
        table_body = table.find('tbody')
        table_row_data = table_body.find_all('tr')
        
        j = 0
        for j in range(len(table_row_data)):
            table_td_data = table_row_data[j].find_all('td', {'class': 'table_cells'})
            data = []
            data.append((cnt + j))
            data.append(store_data[0])
            
            for i in range(len(table_td_data)):
                data.append(table_td_data[i].text)
            sub_data.append(data)
        
        cnt += (j + 1)
    
    global store_sub_data
    store_sub_data = temp_store_data_by_date
    return store_sub_data

# export excel file
def export_csv_file():
    global total_data
    temp_total_data = total_data
    document_folder = pathlib.Path.home() / "Documents"
    filename = 'anaslo_data.xls'
    filepath = document_folder / filename
    
    with open(filepath, 'wb') as file:
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet("sheet", cell_overwrite_ok=True)
        style = xlwt.Style()
        font = xlwt.Font()
        
        count = 0
        for region in region_list_data:
            font.bold = True
            font.height = 320
            style.font = font
            sheet.write(count, 0, region[0], style=style)
            sheet.write(count, 1, region[2], style=style)
            count += 1
            
            for store in store_list_data:
                font.bold = True
                font.height = 280
                style.font = font
                if store[1] == region[0]:
                    sheet.write(count, 0, store[0], style=style)
                    sheet.write(count, 1, store[3], style=style)
                    sheet.write(count, 2, store[4], style=style)
                    count += 1
                    
                for store_data in store_data_by_date:
                    font.bold = True
                    font.height = 240
                    style.font = font
                    if store_data[1] == store[0]:
                        sheet.write(count, 0, store_data[3], style=style)
                        sheet.write(count, 1, store_data[4], style=style)
                        sheet.write(count, 2, store_data[5], style=style)
                        sheet.write(count, 3, store_data[6], style=style)
                        sheet.write(count, 4, store_data[7], style=style)
                        count += 1
                        
                    for sub_data in store_sub_data:
                        font.height = 240
                        style.font = font
                        if sub_data[1] == store_data[0]:
                            for i in range(len(sub_data)):
                                if i < (i - 2):
                                    sheet.write(count, i, store_sub_data[i + 2], style=style)
                            count += 1

    return

# save data in database
def save_data_in_database():
    cnx = None
    try:
        cnx = mysql.connector.connect(host=conf.DB_HOST, user=conf.DB_USER, password=conf.DB_PWD, database=conf.DB_NAME)
        cursor = cnx.cursor()
        cursor.execute("TRUNCATE TABLE tbl_region")
        cursor.execute("TRUNCATE TABLE tbl_store_list")
        cursor.execute("TRUNCATE TABLE tbl_store_data_by_date")
        cursor.execute("TRUNCATE TABLE tbl_model_data")
        
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        if cnx != None:
            cnx.close()