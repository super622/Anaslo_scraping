import asyncio
import math
import time
import sys
import xml.etree.ElementTree as ET
import mysql.connector
import requests
import config
import _thread as thread

from bs4 import BeautifulSoup
from sp_api.api import FeedsV2
from sp_api.base.marketplaces import Marketplaces

class UploadProduct:
    def __init__(self, products_list):
        self.products_list = products_list
        
        self.merchant_name = config.MERCHANT_NAME
        self.merchant_id = config.MAKETPLACEID
        self.credentials = config.CREDENTIALS

    # Get Feed Result
    async def get_feed_result(self, feedId):
        access_token = await self.get_access_token()
        url = f'https://sellingpartnerapi-fe.amazon.com/feeds/2021-06-30/feeds/{feedId}'
        headers = {
            "x-amz-access-token": access_token,
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_response = response.json()
            if json_response['processingStatus'] == 'DONE':
                return [json_response['processingStatus'], json_response['resultFeedDocumentId']]
            else:
                return ['', '']
        else:
            sys.exit(1)

    # Product upload
    async def upload(self, type):
        credentials = self.credentials
        contentType = "text/xml;charset=utf-8"
        obj = FeedsV2(marketplace=Marketplaces.JP, credentials=credentials)
        feed_type = type
        file = open(f"./{type}.xml", "rb")
        try:
            result = obj.submit_feed(feed_type=feed_type, file=file, content_type=contentType)
            payload = result[1].payload
            
            if 'feedId' in payload:
                feed_id = payload['feedId']
                feed_res = ''
                document_id = ''
                while feed_res != 'DONE':
                    time.sleep(10)
                    res = await self.get_feed_result(feed_id)
                    feed_res = res[0]
                    document_id = res[1]
                print('=================================================================')
                print(feed_res)
                print(document_id)
                print('=================================================================')
            else:
                print("No 'feedId' found in the 'ApiResponse' object.")
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)
            await self.upload(type)

    # Get Product title
    async def getTitle(self, asin):
        access_token = await self.get_access_token()
        url = "https://sellingpartnerapi-fe.amazon.com/catalog/2022-04-01/items"
        headers = {
            "x-amz-access-token": access_token,
            "Accept": "application/json"
        }
        params = {
            "marketplaceIds": config.MAKETPLACEID,
            "sellerId": config.SELLERID,
            "includedData": "attributes",
            "identifiersType": "ASIN",
            "identifiers": asin
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            if(json_response['items']):
                return json_response['items'][0]['attributes']['item_name'][0]['value']
            else:
                return ''
        else:
            sys.exit(1)

    # Get ISBN from ASIN
    async def getISBN(self, ASIN):
        access_token = await self.get_access_token()
        url = "https://sellingpartnerapi-fe.amazon.com/catalog/2022-04-01/items"
        headers = {
            "x-amz-access-token": access_token,
            "Accept": "application/json"
        }
        params = {
            "marketplaceIds": config.MAKETPLACEID,
            "sellerId": config.SELLERID,
            "includedData": "identifiers",
            "identifiersType": "ISBN",
            "identifiers": ASIN
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            return json_response['items'][0]['identifiers'][0]['identifiers'][1]['identifier']
        else:
            sys.exit(1)

    # Get an access token to use the amazon sp api
    async def get_access_token(self):
        url = "https://api.amazon.co.jp/auth/o2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": config.REFRESH_TOKEN,
            "scope": "sellingpartnerapi::migration",
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            json_response = response.json()
            return json_response["access_token"]
        else:
            sys.exit(1)

    # Get Price of Other sellers
    async def getCompetitivePrice(self, asin):
        access_token = await self.get_access_token()
        url = "https://sellingpartnerapi-fe.amazon.com/products/pricing/v0/competitivePrice"
        headers = {
            "x-amz-access-token": access_token,
            "Accept": "application/json"
        }
        params = {
            "MarketplaceId": config.MAKETPLACEID,
            "Asins": asin,
            "ItemType": 'Asin',
            "ItemCondition": 'New'
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            if(json_response['payload'][0]['Product']['CompetitivePricing']['CompetitivePrices']):
                return json_response['payload'][0]['Product']['CompetitivePricing']['CompetitivePrices'][0]['Price']['LandedPrice']['Amount']
            else:
                return 0
        else:
            sys.exit(1)

    # Get Data from purpose site
    async def scanData(self, data):
        # Send get request
        async def send_request(p_url, p_param):
            url = p_url
            headers = {
                'Content-Type': 'application/json',
                "Accept": "application/json",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            }
            param = p_param

            response = requests.get(url, params=param, headers=headers)
            if response.status_code == 200:
                json_response = response.text
                return json_response
            else:
                sys.exit(1)

        url = 'https://honto.jp/netstore/search.html'
        param = {
            "detailFlg": "1",
            "isbn": data,
            "prdNm": "",
            "seldt": "2026/all/all/before",
            "srchf": "1",
            "store": "1"
        }
        page_content = await send_request(url, param)

        soup = BeautifulSoup(page_content, 'html.parser')
        desired_element = soup.find_all('a', {'class': 'dyTitle'})

        if (len(desired_element) > 1):
            for i in range(len(desired_element)):
                if desired_element[i]['href'].find("book_") != -1:
                    attribute_value = desired_element[i]['href']
        elif (len(desired_element) == 1):
            if desired_element[0]['href']:
                attribute_value = desired_element[0]['href']
            else:
                attribute_value = desired_element['href']
        else:
            return ''

        if(attribute_value.find("book_") != -1):
            start_index = attribute_value.index("book_") + len("book_")
            end_index = attribute_value.index(".html")

            attribute_value = attribute_value[start_index:end_index]
            attribute_value = 'https://honto.jp/netstore/pd-store_06' + attribute_value + '.html'

            page_content = await send_request(attribute_value, {})

            # get product name
            soup = BeautifulSoup(page_content, 'html.parser')
            parent_element = soup.find('h3', {'class': 'stHeading'})
            product_name = parent_element.find('a').get_text()

            # get product price
            parent_element = soup.find('span', {'class': 'stYen'})
            product_price = parent_element.find('span').get_text()

            # get product amount
            element = soup.find_all('span', {'class': 'stIconStock03'})
            product_qty = len(element)

            return {
                'name': product_name,
                'price': product_price,
                'qty': product_qty
            }
        else:
            return ''

    # Get formula information for price calculation
    def get_price_data(self, conditions):
        try:
            with mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PWD,
                database=config.DB_NAME
            ) as cnx:
                cursor = cnx.cursor()

                query = "SELECT * FROM base_settings"
                cursor.execute(query)
                result = cursor.fetchall()

                for row in result:
                    result = row
                
                cursor.close()
                cnx.close()
                if(conditions == 'min_param_1'):
                    return result[2]
                elif(conditions == 'min_param_2'):
                    return result[3]
                elif(conditions == 'max_param'):
                    return result[4]
                elif(conditions == 'reduced_price'):
                    return result[1]
        except Exception as e:
            print(e)
            sys.exit(1)

    # Get Inventory of product
    async def getQty(self, asin):
        ISBN = await self.getISBN(asin)
        scap_data = await self.scanData(ISBN)
        if(scap_data == ''):
            return '0'
        qty = scap_data['qty']
        if(qty > 0):
            qty = 1

        return str(qty)

    # Get price of product
    async def getPrice(self, asin, price):
        ISBN = await self.getISBN(asin)
        other_price = await self.getCompetitivePrice(asin)
        scap_data = await self.scanData(ISBN)
        my_price = price
        
        if(scap_data != ''):
            other_seller_price = int(other_price)
            purchase_price = scap_data['price']
            min_param_1 = self.get_price_data('min_param_1')
            min_param_2 = self.get_price_data('min_param_2')
            max_param = self.get_price_data('max_param')
            reduced_price = self.get_price_data('reduced_price')
            purchase_price = float(purchase_price.replace(',', ''))
            min_price = purchase_price * float(min_param_1) + int(min_param_2)
            max_price = min_price + int(max_param)
            
            if(other_seller_price > min_price and other_seller_price < max_price):
                if(other_seller_price != 0):
                    my_price = math.ceil(other_seller_price - int(reduced_price))
            
            if(other_seller_price < min_price):
                my_price = math.ceil(min_price)
            
            if(other_seller_price > max_price):
                my_price = math.ceil(max_price)
            
        return my_price
        
    # Create XML file
    async def createXmlFile(self, type, products_list):
        if(type == 'POST_PRODUCT_DATA'):
            mytree = ET.parse(f'{type}.xml')
            myroot = mytree.getroot()

            while True:
                messagetag = myroot.find("Message")
                if messagetag is not None:
                    myroot.remove(messagetag)
                else:
                    break
            
            for item in products_list:
                print(item)
                title = await self.getTitle(item[1])

                if(title == ''):
                    return 'ASIN情報が正しくありません。'
            
                message_tag = ET.Element("Message")
                messageId_tag = ET.Element("MessageID")
                messageId_tag.text = str(products_list.index(item) + 1)
                message_tag.append(messageId_tag)

                operationType_tag = ET.Element("OperationType")
                operationType_tag.text = "Update"
                message_tag.append(operationType_tag)

                product_tag = ET.Element("Product")

                sku_tag = ET.Element("SKU")
                sku_tag.text = item[0]
                product_tag.append(sku_tag)

                standardProductID_tag = ET.Element("StandardProductID")
                type_tag = ET.Element("Type")
                type_tag.text = "ASIN"
                standardProductID_tag.append(type_tag)

                value_tag = ET.Element("Value")
                value_tag.text = item[1]
                standardProductID_tag.append(value_tag)
                product_tag.append(standardProductID_tag)

                condition_tag = ET.Element("Condition")
                conditionType_tag = ET.Element("ConditionType")
                conditionType_tag.text = "New"
                condition_tag.append(conditionType_tag)

                conditionNote_tag = ET.Element("ConditionNote")
                conditionNote_tag.text = item[2]
                condition_tag.append(conditionNote_tag)

                descriptionData_tag = ET.Element("DescriptionData")
                title_tag = ET.Element("Title")
                title_tag.text = title
                descriptionData_tag.append(title_tag)

                merchantShippingGroupName_tag = ET.Element("MerchantShippingGroupName")
                merchantShippingGroupName_tag.text = config.MERCHANT_NAME
                descriptionData_tag.append(merchantShippingGroupName_tag)
                product_tag.append(condition_tag)
                product_tag.append(descriptionData_tag)

                message_tag.append(product_tag)
                myroot.append(message_tag)
        elif type == 'POST_INVENTORY_AVAILABILITY_DATA':
            mytree = ET.parse(f'{type}.xml')
            myroot = mytree.getroot()
            
            while True:
                messagetag = myroot.find("Message")
                if messagetag is not None:
                    myroot.remove(messagetag)
                else:
                    break
            
            for item in products_list:
                print(item)
                qty = await self.getQty(item[1])
                
                message_tag = ET.Element("Message")
                messageId_tag = ET.Element("MessageID")
                messageId_tag.text = str(products_list.index(item) + 1)
                message_tag.append(messageId_tag)

                operationType_tag = ET.Element("OperationType")
                operationType_tag.text = "Update"
                message_tag.append(operationType_tag)

                inventory_tag = ET.Element("Inventory")
                sku_tag = ET.Element("SKU")
                sku_tag.text = item[0]
                inventory_tag.append(sku_tag)

                quantity_tag = ET.Element("Quantity")
                quantity_tag.text = str(qty)
                inventory_tag.append(quantity_tag)

                fulfillmentLatency_tag = ET.Element("FulfillmentLatency")
                fulfillmentLatency_tag.text = "5"
                inventory_tag.append(fulfillmentLatency_tag)

                message_tag.append(inventory_tag)
                myroot.append(message_tag)
        elif type == 'POST_PRODUCT_PRICING_DATA':
            mytree = ET.parse(f'{type}.xml')
            myroot = mytree.getroot()
            
            while True:
                messagetag = myroot.find("Message")
                if messagetag is not None:
                    myroot.remove(messagetag)
                else:
                    break

            for item in products_list:
                print(item)
                new_price = await self.getPrice(item[1], item[3])

                message_tag = ET.Element("Message")
                messageId_tag = ET.Element("MessageID")
                messageId_tag.text = str(products_list.index(item) + 1)
                message_tag.append(messageId_tag)

                operationType_tag = ET.Element("OperationType")
                operationType_tag.text = "Update"
                message_tag.append(operationType_tag)

                price_tag = ET.Element("Price")
                sku_tag = ET.Element("SKU")
                sku_tag.text = item[0]
                price_tag.append(sku_tag)

                standardPrice_tag = ET.Element("StandardPrice", {"currency": "JPY"})
                standardPrice_tag.text = str(new_price)
                price_tag.append(standardPrice_tag)

                message_tag.append(price_tag)
                myroot.append(message_tag)

        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml_content = ET.tostring(myroot, encoding='utf-8').decode('utf-8')

        # Write the modified XML content with the declaration to a new file using UTF-8 encoding
        with open(f'{type}.xml', 'w', encoding='utf-8') as output_file:
            output_file.write(xml_declaration + xml_content)

    # Change credentials
    def change_credentials(self, type):
        if(type == "POST_PRODUCT_DATA"):
            self.credentials = config.CREDENTIALS_1
        elif(type == "POST_INVENTORY_AVAILABILITY_DATA"):
            self.credentials = config.CREDENTIALS_2
        elif(type == "POST_PRODUCT_PRICING_DATA"):
            self.credentials = config.CREDENTIALS_1

    async def main(self):
        type_array = [
            "POST_PRODUCT_DATA",
            "POST_INVENTORY_AVAILABILITY_DATA",
            "POST_PRODUCT_PRICING_DATA"
        ]
        for type in type_array:
            print(type)
            await self.createXmlFile(type, self.products_list)
            self.change_credentials(type)
            await self.upload(type)
            time.sleep(5)
        return 'success'

    def run(self):
        result = asyncio.run(self.main())
        return result
