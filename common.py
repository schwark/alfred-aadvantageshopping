# encoding: utf-8

import os
import json
import time
import random
import datetime
from workflow import ICON_WEB, Workflow, web
from brands import BRANDS, get_brand_config

def get_random_user_agent():
    """Get a random but realistic user agent string."""
    user_agents = [
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15',
        # Firefox on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
        # Edge on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
    ]
    return random.choice(user_agents)

def get_bonus_percentage(store):
    """Calculate bonus percentage as percentage increase over regular rate.
    For example: if regular rate is 2% and current rate is 5%,
    bonus is (5-2)/2 * 100 = 150% increase"""
    rebate = store['rebate']
    if not rebate['isElevation']:
        return 0
    
    def parse_value(val):
        if isinstance(val, (int, float)):
            return float(val)
        return float(str(val).replace('%', ''))
    
    current = parse_value(rebate['value'])
    original = parse_value(rebate['originalValue'])
    if original == 0:  # avoid division by zero
        return 0
    return ((current - original) / original) * 100

def get_stores_from_api(brand_config):
    """Fetch stores from API."""
    params = {
        'brand_id': brand_config['brand_id'],
        'app_key': brand_config['app_key'],
        'app_id': brand_config['app_id'],
        'limit': 2000,
        'sort_by': 'name',
        'fields': 'name,type,id,clickUrl,synonyms,showRebate,rebate,logoUrls._120x60,relatedActiveMerchants,categories',
        'include_inactive': 0
    }
    
    # Add section_id if it exists for the brand
    if 'section_id' in brand_config:
        params['section_id'] = brand_config['section_id']
    
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': brand_config['url'],
        'Host': 'api.cartera.com',
        'User-Agent': get_random_user_agent(),
        'Referer': brand_config['url'],
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        r = web.get(url='https://api.cartera.com/content/v4/merchants', headers=headers, params=params)
        r.raise_for_status()  # Raise an exception for bad status codes
        
        if not r.content:
            wf.logger.error("Empty response from API")
            return None
            
        data = r.json()
        if not isinstance(data, dict) or 'response' not in data:
            wf.logger.error("Invalid response format from API")
            return None
            
        return data['response']
    except Exception as e:
        wf.logger.error(f"Error fetching stores: {e}")
        return None

def get_stores(force_update=False):
    """Get stores from cache or update if needed."""
    wf = Workflow()
    
    # Check if we need to update
    last_update = get_stored_data(wf, 'last_update') or 0
    if isinstance(last_update, datetime.datetime):
        last_update = int(last_update.timestamp())
    now = int(datetime.datetime.now().timestamp())
    
    # Update if forced or more than 24 hours have passed
    if force_update or now - last_update > 24 * 60 * 60:
        try:
            # Get current brand
            current_brand = get_stored_data(wf, 'current_brand')
            if isinstance(current_brand, bytes):
                current_brand = current_brand.decode('utf-8')
            
            # Get brand configuration
            brand_config = BRANDS.get(current_brand)
            if not brand_config:
                raise ValueError(f"Invalid brand: {current_brand}")
            
            # Get stores from API
            stores = get_stores_from_api(brand_config)
            
            # Calculate bonus percentage for each store
            for store in stores:
                store['bonus_percentage'] = get_bonus_percentage(store)
            
            # Store updated data
            wf.store_data('stores', stores)
            wf.store_data('last_update', datetime.datetime.now())
            
            return stores
            
        except Exception as e:
            wf.logger.error(f"Error updating stores: {e}")
            # If update fails, try to return cached data
            stores = get_stored_data(wf, 'stores')
            if stores:
                return stores
            raise
    
    # Return cached data if available
    stores = get_stored_data(wf, 'stores')
    if stores:
        return stores
    
    # If no cached data, force an update
    return get_stores(force_update=True)

def get_logo_file(wf, store):
    filename = wf.datafile(str(store['id'])+'.jpg')
    return filename

def get_stored_data(wf, key):
    """Retrieve stored data for the given key."""
    try:
        data = wf.stored_data(key)
        return data
    except Exception as e:
        wf.logger.error(f'Error retrieving {key}: {str(e)}')
        return None

def save_stored_data(wf, key, data):
    """Save data for the given key."""
    try:
        wf.store_data(key, data)
        return True
    except Exception as e:
        wf.logger.error(f'Error saving {key}: {str(e)}')
        return False

def get_buttons(wf):
    """Get all web buttons."""
    return get_stored_data(wf, 'buttons') or []

def save_button(wf, name, url, tags=None):
    """Save a new web button."""
    buttons = get_buttons(wf)
    button = {
        'id': len(buttons),
        'name': name,
        'url': url,
        'tags': tags or []
    }
    buttons.append(button)
    return save_stored_data(wf, 'buttons', buttons)

def delete_button(wf, button_id):
    """Delete a web button."""
    buttons = get_buttons(wf)
    buttons = [b for b in buttons if b['id'] != button_id]
    return save_stored_data(wf, 'buttons', buttons)

def get_icon(wf, button):
    """Get the icon for a button."""
    return ICON_WEB  # Default web icon

