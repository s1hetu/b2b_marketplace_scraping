"""
Defining items for scrapy
"""
import scrapy


class ProductScraperItem(scrapy.Item):
    """
    Scrapy Item to load data.
    """
    vendorId = scrapy.Field()
    searchQuery = scrapy.Field()
    regionSearchedFor = scrapy.Field()
    companyName = scrapy.Field()
    companyUrl = scrapy.Field()
    companyRegion = scrapy.Field()
    productUrl = scrapy.Field()
    companyContactNumber = scrapy.Field()
    stars = scrapy.Field()
    users_count = scrapy.Field()
    verifier_name = scrapy.Field()
    call_response_rate = scrapy.Field()
    product_images = scrapy.Field()
    product_specs = scrapy.Field()
    seller_name = scrapy.Field()
    gmaps = scrapy.Field()
    product_description = scrapy.Field()
    company_url = scrapy.Field()
    company_details = scrapy.Field()
    company_address = scrapy.Field()
    company_description = scrapy.Field()
    category = scrapy.Field()
