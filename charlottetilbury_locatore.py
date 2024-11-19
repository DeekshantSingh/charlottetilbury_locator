import requests
from parsel import Selector
import re

# Define constants for cookies and headers
COOKIES = {
    '_ga': 'GA1.2.26063726.1732012493',
    '_gid': 'GA1.2.1983368387.1732012493',
    'OptanonAlertBoxClosed': '2024-11-19T10:35:07.381Z',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Nov+19+2024+16%3A06%3A30+GMT%2B0530+(India+Standard+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=26fc6368-02df-4e82-9c5e-587411d5f091&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&intType=1',
}

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.google.com/',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}


def fetch_urls(base_url):
    """Fetch all URLs from the main page."""
    response = requests.get(base_url, cookies=COOKIES, headers=HEADERS)
    parsed_data = Selector(response.text)
    return parsed_data.xpath(
        '//ul[@class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 p-0 my-0 gap-x-0 text-left"]//li//@href').getall()


def separate_address_and_contact(data):
    """Separates address and contact details from a given list."""
    phone_pattern = r'\(\d{3}\)\s\d{3}-\d{4}'  # Matches (XXX) XXX-XXXX format
    address, contact = [], []

    for item in data:
        if re.search(phone_pattern, item):  # Check if the item matches the phone pattern
            contact.append(item)
        else:
            address.append(item)

    return ' '.join(address), ' '.join(contact)


def parse_store_details(store, base_url):
    """Extract and format store details, along with XPath and HTML."""
    # Store name
    store_name_xpath = './/h2/text()'
    store_name = ''.join(store.xpath(store_name_xpath).getall()).replace('-', '').strip()
    store_name_html = store.xpath(store_name_xpath).getall()
    store_name = ' '.join(store_name.split())  # Clean up extra spaces

    # Store URL
    store_url_xpath = './/a[@class="Link"]//@href'
    store_url = store.xpath(store_url_xpath).get()
    store_url_html = store.xpath(store_url_xpath).get()
    store_url = base_url + store_url.replace('.', '').replace('//', '')

    # Address and contact
    address_xpath = './/div[@class="mb-4"]//text()'
    addresses = store.xpath(address_xpath).getall()
    address, contact = separate_address_and_contact(addresses)
    address_html = store.xpath(address_xpath).getall()
    address = ' '.join(address.split()).strip()
    contact = contact.strip()

    return {
        "Store_name": store_name,
        "Store_name_xpath": store_name_xpath,
        "Store_name_html": store_name_html,
        "store_url": store_url,
        "store_url_xpath": store_url_xpath,
        "store_url_html": store_url_html,
        "Address": address,
        "Address_xpath": address_xpath,
        "Address_html": address_html,
        "Contact": contact,
    }


def process_stores(base_url, urls):
    """Iterate through URLs and extract details for each store."""
    store_details_list = []

    for url in urls:
        first_page_url = base_url + url.replace('.', '')
        response2 = requests.get(first_page_url, headers=HEADERS, cookies=COOKIES)
        parsed_data2 = Selector(response2.text)

        second_page_urls = parsed_data2.xpath(
            '//ul[@class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 p-0 my-0 gap-x-0 text-left"]//li//@href').getall()
        for s_url in second_page_urls:
            second_page_url = base_url + s_url.replace('.', '')
            response3 = requests.get(second_page_url, headers=HEADERS, cookies=COOKIES)
            parsed_data3 = Selector(response3.text)

            stores = parsed_data3.xpath('//div[@class="w-full sm:w-[calc(50%-24px)] lg:w-[calc(33.33%-24px)]"]')
            for store in stores:
                details = parse_store_details(store, base_url)
                store_details_list.append(details)
                print(details)

    return store_details_list


def main():
    """Main function to orchestrate scraping."""
    base_url = 'https://stores.charlottetilbury.com'
    initial_url = f'{base_url}/en-us/us'

    print("Fetching initial URLs...")
    urls = fetch_urls(initial_url)
    print(f"Found {len(urls)} URLs.")

    print("Processing store details...")
    store_details = process_stores(base_url, urls)

    print("Extracted Store Details:")
    for details in store_details:
        print(details)


if __name__ == "__main__":
    main()
