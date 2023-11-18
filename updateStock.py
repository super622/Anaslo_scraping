import time
import requests
import asyncio
import config

from sp_api.api import FeedsV2
from sp_api.base.marketplaces import Marketplaces

class ProductUpdater:
    def __init__(self, sku):
        self.sku = sku
    
    async def updatePriceAndStock(self, product_id):
        def make_request(url, data, headers):
            retries = 0
            while True:
                try:
                    response = requests.put(url, data=data, headers=headers)
                    return response
                except requests.exceptions.ConnectionError as e:
                    print(f"ConnectionError: {e}")
                    retries += 1
                    backoff_delay = 3 ** retries
                    time.sleep(backoff_delay)

        credentials = config.CREDENTIALS
        contentType = 'text/tab-separated-values'
        obj = FeedsV2(marketplace=Marketplaces.JP, credentials=credentials)

        result = obj.create_feed_document(file=None, content_type=contentType)
        feedDocumentId = result.payload["feedDocumentId"]
        url = result.payload["url"]
        stock = 1
        feed_data = f'sku\tquantity\n{product_id}\t{stock}'
        upload = make_request(url, feed_data, {"Content-Type": contentType})
        feed_type = "POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA"
        if 200 <= upload.status_code < 300:
            retries = 0
            while 1:
                try:
                    obj.create_feed(feed_type=feed_type, input_feed_document_id=feedDocumentId)
                    return ("success")
                except Exception as e:
                    print(f"{e}")
                    retries += 1
                    backoff_delay = 3 ** retries
                    time.sleep(backoff_delay)
        else:
            print("failed")

    async def main(self):
        result = await self.updatePriceAndStock(self.sku)
        return result

    def run(self):
        result = asyncio.run(self.main())
        return result
