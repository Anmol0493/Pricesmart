from helper_class import *
import pandas, time
from proxy_interface import *


class PriceMart():

    def __init__(self):
        
        self.helper = Helper()
        self.proxy = CWEBSHARE()

        self.proxy_filename = "proxy.json"
        self.proxy.get_proxy_list(self.proxy_filename)
        self.all_proxies = self.helper.read_json_file(self.proxy_filename)["proxies"]
        self.valid_proxies = [proxy for proxy in self.all_proxies if proxy["valid"]]

        with open("config.json") as configfile:
            self.config = json.load(configfile)

        self.location = self.config["Portmore_club"]

        self.cookies = {'userPreferences': f'country=jm&lang=en&selectedClub={self.location}'}

        self.MAX_WORKERS = self.config["MAX_WORKERS"]

        self.products_urls = []

        with open('product_info.json') as json_file:
            self.product_info = json.load(json_file)

        self.details = []

        self.success = []

        self.error_url = []


    def getProxy(self):
        proxy = random.choice(self.valid_proxies)
        proxyHandler = f'http://{proxy["username"]}:{proxy["password"]}@{proxy["proxy_address"]}:{proxy["ports"]["http"]}'
        return {"https": proxyHandler, "http": proxyHandler}


    def run_multithread(self, function, argument):

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            executor.map(function, argument)


    def get_product_url(self, c_url):

        page = 1

        while True:
            c_re = requests.get(c_url+f"&r130_r1_r3_r1:page={page}&r130_r1_r3_r1:_sps=12", proxies=self.getProxy())
            print(c_url, page, c_re.status_code)
            if c_re.status_code == 200:
                c_soup = BeautifulSoup(c_re.content, "lxml")

                if "Sorry! We couldn't find what you were looking for. Please try again using a different keyword" in str(c_soup):
                    break

                category = self.helper.get_text_from_tag(c_soup.find("title")).split(" |")[0].replace(",", "|").replace("&", "|")

                result = c_soup.find("div", {"id": "page-content-wrapper"})
                urls = [{"category": category, "url": "https://www.pricesmart.com" + x.find("a").get("href")} for x in result.find_all("div", {"class": "search-product-box"})]
                self.products_urls.extend(urls)

            page += 1


    def scarp_product_details(self, obj):

        p_url = obj["url"]
        category = obj["category"]
        p_re = requests.get(p_url, cookies=self.cookies, proxies=self.getProxy())
        print(p_url, p_re.status_code)

        try:

            if p_re.status_code == 200:
                p_soup = BeautifulSoup(p_re.content, "lxml")
                # today = datetime.datetime.now()
                product_info = self.product_info.copy()

                product_info["sku"] = self.helper.get_text_from_tag(p_soup.find("label", {"id": "itemNumber"}))

                product_info["attribute_set_code"] = self.config["attribute_set_code_prefix"]
                product_info["product_type"] = self.config["product_type_prefix"]
                product_info["categories"] = self.config["Category_prefix"] + category
                product_info["product_websites"] = self.config["product_websites_prefix"]

                name = self.helper.get_text_from_tag(p_soup.find("title")).split("|")[0].strip()
                product_info["name"] = ''.join(char for char in name if ord(char) < 128).replace("Members", "").replace("Member's", "").replace("Member", "").strip()

                product_info["product_online"] = self.config["product_online_prefix"]

                try:
                    price = self.helper.get_text_from_tag(p_soup.find("strong", {"id": "product-price"}))
                    if price == "":
                        if p_soup.find("i", {"class": "fa fa-check"}).get("style") != "color:red":
                            p_re_ = requests.get(p_url, cookies={'userPreferences': f'country=jm&lang=en&selectedClub={self.config["Kingstone_club"]}'}, proxies=self.getProxy())
                            p_soup_ = BeautifulSoup(p_re_.content, "lxml")
                            price = self.helper.get_text_from_tag(p_soup_.find("strong", {"id": "product-price"}))
                    product_info["additional_attributes"] = self.config["additional_attributes_prefix"].replace("{price}", str(price))
                    product_info["price"] = round(float(price) * self.config["Variable_X"], 2)

                except:
                    pass

                # # product_info["special_price_from_date"] = today.strftime("%d-%m-%Y")
                # # product_info["special_price_to_date"] = today.strftime("%d-%m-%Y")

                product_info["description"] = self.helper.get_text_from_tag(p_soup.find("div", {"id": "product-description"})).replace("PriceSmart", "Virtual Mart").replace("Pricesmart", "Virtual Mart").replace("PRICESMART", "Virtual Mart")

                product_info["short_description"] = category

                product_info["url_key"] = product_info["name"] + "-" + product_info["sku"]

                product_info["meta_title"] = product_info["name"]
                product_info["meta_keywords"] = product_info["name"]
                product_info["meta_description"] = product_info["name"]

                download_dir = os.path.join("Images", product_info["sku"])
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                img_cont = p_soup.find("div", {"class":"product-thumb-cont"})
                defaultImage_srcs = [x.get("src") for x in img_cont.find_all("img", {"class": "product-thumb-item-img"})]

                additional_images = []

                for index, src in enumerate(defaultImage_srcs):
                    defaultImage_re = requests.get(src)

                    if defaultImage_re.status_code == 200:
                        filename = os.path.join(download_dir, f'W{product_info["sku"]}_{index+1}.jpg')

                        with open(filename, 'wb') as defaultImage:
                            defaultImage.write(defaultImage_re.content)

                        additional_images.append(f'W{product_info["sku"]}_{index+1}.jpg')

                product_info["base_image"] = f'W{product_info["sku"]}_1.jpg'
                product_info["small_image"] = product_info["base_image"]
                product_info["thumbnail_image"] = product_info["base_image"]
                product_info["swatch_image"] = product_info["base_image"]
                product_info["additional_images"] = ','.join(additional_images)

                product_info["visibility"] = self.config["visibility_prefix"]

                # product_info["qty"] = "0" if self.helper.get_text_from_tag(p_soup.find("span", {"id": "clubQuantity"})) == "" else "10000"
                product_info["qty"] = "10000" if p_soup.find("div", {"class": "input-group"}) else "0"
                if product_info["qty"] == "0":
                    available_row = p_soup.find("div", {"class": "col-12 p-0"}).find_all("p", {"class": "text-left"})
                    available = [x.text.strip() for x in available_row if x.find("i").get("style") == "color:#7ED321"]
                    if len(available) > 0:
                        product_info["qty"] = "10000"

                product_info["total_qty"] = product_info["qty"]

                product_info["out_of_stock_qty"] = self.config["out_of_stock_qty_prefix"]
                product_info["use_config_min_qty"] = self.config["use_config_min_qty_prefix"]
                product_info["is_qty_decimal"] = self.config["is_qty_decimal_prefix"]
                product_info["allow_backorders"] = self.config["allow_backorders_prefix"]
                product_info["use_config_backorders"] = self.config["use_config_backorders_prefix"]
                product_info["min_cart_qty"] = self.config["min_cart_qty_prefix"]
                product_info["use_config_min_sale_qty"] = self.config["use_config_min_sale_qty_prefix"]

                product_info["max_cart_qty"] = product_info["qty"]
                product_info["use_config_max_sale_qty"] = self.config["use_config_max_sale_qty_prefix"]

                product_info["is_in_stock"] = "0" if product_info["qty"] == "0" else "1"

                product_info["notify_on_stock_below"] = self.config["notify_on_stock_below_prefix"]
                product_info["use_config_notify_stock_qty"] = self.config["use_config_notify_stock_qty_prefix"]
                product_info["manage_stock"] = self.config["manage_stock_prefix"]
                product_info["use_config_manage_stock"] = self.config["use_config_manage_stock_prefix"]
                product_info["use_config_qty_increments"] = self.config["use_config_qty_increments_prefix"]
                product_info["qty_increments"] = self.config["qty_increments_prefix"]
                product_info["use_config_enable_qty_inc"] = self.config["use_config_enable_qty_inc_prefix"]
                product_info["enable_qty_increments"] = self.config["enable_qty_increments_prefix"]
                product_info["is_decimal_divided"] = self.config["is_decimal_divided_prefix"]

                product_info["qty_2"] = product_info["qty"]
                product_info["qty_8"] = product_info["qty"]

                self.details.append(product_info)
                self.success.append(p_url)
                print(len(self.details))

        except Exception as e:
            self.error_url.append(obj)
            print(p_url, e)


    def run(self):

        start_time = time.time()

        url = "https://www.pricesmart.com/site/jm/en"

        re = requests.get(url)

        if re.status_code == 200:
            soup = BeautifulSoup(re.content, "lxml")

            categories_html = soup.find("div", {"id": "categories-section"})
            categories = ["https://www.pricesmart.com" + x.get("href") for x in categories_html.find_all("a", {"class": "categories-section-link"})[1::]]
            print("Total categories:", len(categories))

            for cate in categories:
                if "groceries" in cate:
                    c_re = requests.get(cate, proxies=self.getProxy())
                    if c_re.status_code == 200:
                        c_soup = BeautifulSoup(c_re.content, "lxml")
                        result = c_soup.find("ul", {"id": "categories-section2"})
                        sub_category = ["https://www.pricesmart.com"+ x.find("a").get("href") for x in result.find_all("li", {"class": "heading-category"})]
                        self.run_multithread(self.get_product_url, sub_category)
                        categories.remove(cate)
                    break

            self.run_multithread(self.get_product_url, categories)
            print('\033[93m' + f"Product urls: {len(self.products_urls)}"+ '\033[0m')

            self.run_multithread(self.scarp_product_details, self.products_urls)

            count = 1
            while count < 3:
                error_urls = self.error_url
                self.error_url = []
                for i in error_urls:
                    self.scarp_product_details(i)
                count += 1

            failed_urls = list(set([x["url"] for x in self.products_urls]) - set(self.success))
            with open("Failed_urls.json", "w") as f:
                json.dump(failed_urls, f, indent=4)

            print('\033[93m' + f"Product urls: {len(self.products_urls)}"+ '\033[0m')
            print('\033[93m' + f"Scraped Products: {len(self.details)}" + '\033[0m')
            failed = len(self.products_urls) - len(self.details)
            print('\033[93m' + f"Failed products: {failed}" + '\033[0m')

            df = pandas.DataFrame(self.details)
            df_ = df.drop_duplicates()
            df_.to_csv(f"{self.config['CSV_filename']}.csv", header=True, index=False, encoding="utf-8")
            print('\033[92m' + f"{self.config['CSV_filename']}.csv file is created" + '\033[0m')

            end_time = time.time()
            elapsed_time = end_time - start_time
            print('\033[92m' + f"Script executed in {elapsed_time:.2f} seconds" + '\033[0m')


if __name__ == "__main__":
    PriceMart().run()