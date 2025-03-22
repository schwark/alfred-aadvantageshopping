# Brand configurations for different shopping portals
BRANDS = {
    'american': {
        'name': 'American Airlines',
        'shop_name': 'AAdvantage',
        'brand_id': '251',
        'app_key': '9ec260e91abc101aaec68280da6a5487',
        'app_id': '672b9fbb',
        'url': 'https://www.aadvantageeshopping.com',
        'favicon': 'icons/brands/aa.png'
    },
    'united': {
        'name': 'United Airlines',
        'shop_name': 'MileagePlus',
        'brand_id': '227',
        'app_key': 'e890b0f48aa7523311b3218506ee8e8d',
        'app_id': 'c5c10c2a',
        'url': 'https://shopping.mileageplus.com',
        'favicon': 'icons/brands/united.png'
    },
    'delta': {
        'name': 'Delta Air Lines',
        'shop_name': 'SkyMiles',
        'brand_id': '106',
        'app_key': '82f17ef5651e834e5d0d1a7081cb455d',
        'app_id': 'f3cc4f99',
        'url': 'https://www.skymilesshopping.com',
        'favicon': 'icons/brands/delta.png'
    },
    'alaska': {
        'name': 'Alaska Airlines',
        'shop_name': 'MileagePlan',
        'brand_id': '358',
        'app_key': '656a63361c344ee3959f9922be8ab4fe',
        'app_id': '5fe54f2a',
        'url': 'https://www.mileageplanshopping.com',
        'favicon': 'icons/brands/alaska.png'
    },
    'southwest': {
        'name': 'Southwest Airlines',
        'shop_name': 'RapidRewards',
        'brand_id': '247',
        'app_key': '1f5f444ceeb840c9fc14c4a5ca0886d4',
        'app_id': '29d31a15',
        'url': 'https://rapidrewardsshopping.southwest.com',
        'favicon': 'icons/brands/southwest.png'
    },
    'usaa': {
        'name': 'USAA',
        'shop_name': 'MemberShop',
        'brand_id': '137',
        'app_key': 'c2c8a6aa0829a7b3b5030355336942ae',
        'app_id': '7e04dca9',
        'url': 'https://mall.usaa.com',
        'favicon': 'icons/brands/usaa.png'
    },
    'barclays': {
        'name': 'Barclays',
        'shop_name': 'RewardsBoost',
        'brand_id': '356',
        'app_key': '6ceb21f5a77c78b28382e4cbc838497e',
        'app_id': '8a2f6ddd',
        'url': 'https://www.barclaycardrewardsboost.com',
        'favicon': 'icons/brands/barclays.png'
    }
}

def get_brand_config(brand_name):
    """Get configuration for a specific brand."""
    return BRANDS.get(brand_name.lower()) 