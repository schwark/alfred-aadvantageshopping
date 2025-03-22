# encoding: utf-8

import datetime
from multiprocessing.sharedctypes import Value
import sys
import re
import argparse
from os.path import exists
from workflow.workflow import MATCH_ATOM, MATCH_STARTSWITH, MATCH_SUBSTRING, MATCH_ALL, MATCH_INITIALS, MATCH_CAPITALS, MATCH_INITIALS_STARTSWITH, MATCH_INITIALS_CONTAIN
from workflow import Workflow, ICON_WEB, ICON_NOTE, ICON_BURN, ICON_SWITCH, ICON_HOME, ICON_COLOR, ICON_INFO, ICON_SYNC, web, PasswordNotFound
from workflow.util import run_applescript
from common import get_logo_file, get_stored_data, get_stores, get_bonus_percentage
from brands import get_brand_config, BRANDS
import os
import plistlib

log = None

# united, https://shopping.mileageplus.com/, https://api.cartera.com/content/v4/merchants/all?brand_id=227&app_key=e890b0f48aa7523311b3218506ee8e8d&app_id=c5c10c2a&limit=2000&sort_by=name&fields=name%2Ctype%2Cid%2Csynonyms%2CclickUrl%2CshowRebate%2Crebate%2ClogoUrls._88x31%2CisDirect%2Cflags.storesPageApproved%2Cflags.tracksMobile%2CcarteraMerchantId%2Coffers%2CrelatedActiveMerchants&include_inactive=1
# american, https://www.aadvantageeshopping.com, https://api.cartera.com/content/v4/merchants?brand_id=251&app_key=9ec260e91abc101aaec68280da6a5487&app_id=672b9fbb&personalized=rec&limit=14&fields=id%2C+name&mem_id=2fCiDMytn%2FbrgzlQf5%2FxO8rQu0qq0qY6ULIhWHNU9iCxC%2F%2Ba%2F7E8Uvou%2B5I1dIMZS9psVCADl%2FL6hgXSOuajQRXQuPlYirlZCqFvR0E6bDIWwR1hwOE%2BNzM1n%2FqC1tqP07RRgmLqkci2HUDvA0Uot6ggKODOpyqTmEmPdt%2BRL7a9f0LllFD4j86yISTWHZf2gHi%2FkuoLJulALseu5kSStQEl7ciM6HM63sWqG5zZF1o%3D
# delta, https://www.skymilesshopping.com,  https://api.cartera.com/content/v4/merchants?brand_id=106&app_key=82f17ef5651e834e5d0d1a7081cb455d&app_id=f3cc4f99&personalized=rec&limit=14&fields=id%2C+name
# alaska, https://www.mileageplanshopping.com,  https://api.cartera.com/content/v4/merchants?brand_id=358&app_key=656a63361c344ee3959f9922be8ab4fe&app_id=5fe54f2a&personalized=rec&limit=14&fields=id%2C+name
# southwest, https://rapidrewardsshopping.southwest.com, https://api.cartera.com/content/v4/merchants?brand_id=247&app_key=1f5f444ceeb840c9fc14c4a5ca0886d4&app_id=29d31a15&personalized=rec&limit=14&fields=id%2C+name
# usaa, https://mall.usaa.com, https://api.cartera.com/content/v4/merchants?brand_id=137&app_key=c2c8a6aa0829a7b3b5030355336942ae&app_id=7e04dca9&personalized=rec&limit=14&fields=id%2C+name
# barclays, https://www.barclaycardrewardsboost.com,  https://api.cartera.com/content/v4/merchants?brand_id=356&app_key=6ceb21f5a77c78b28382e4cbc838497e&app_id=8a2f6ddd&limit=2000&sort_by=name&fields=name%2Ctype%2Cid%2Csynonyms%2CclickUrl%2CshowRebate%2Crebate%2ClogoUrls._88x31%2CisDirect%2Cflags.storesPageApproved%2Cflags.tracksMobile%2CcarteraMerchantId%2CrelatedActiveMerchants&include_inactive=1

def find_store_by_url(wf, store_url):
    """Find store from store URL."""
    stores = get_stores()
    if not stores:
        return None
    
    # Remove quotes if present
    store_url = store_url.strip('"')
    
    # Find store with matching URL
    for store in stores:
        if store.get('clickUrl') == store_url:
            return store
    return None

def update_brand(wf, brand_name):
    """Update all brand-related settings and files."""
    # Get brand configuration
    brand_config = get_brand_config(brand_name)
    if not brand_config:
        raise ValueError(f"Invalid brand: {brand_name}")
    
    # Store current brand
    wf.store_data('current_brand', brand_name.encode('utf-8'))
    
    # Copy brand icon
    if 'favicon' in brand_config:
        src_icon = wf.workflowfile(brand_config['favicon'])
        dst_icon = wf.workflowfile('icon.png')
        if os.path.exists(src_icon):
            import shutil
            shutil.copy2(src_icon, dst_icon)
    
    # Update info.plist with new brand name and shop name
    info_plist = wf.workflowfile('info.plist')
    if os.path.exists(info_plist):
        with open(info_plist, 'rb') as f:
            plist_data = plistlib.load(f)
        
        # Update description
        plist_data['description'] = f"Alfred Workflow for {brand_config['shop_name']} Shopping"
        
        # Update name
        plist_data['name'] = f"{brand_config['shop_name']} Shopping"
        
        # Update readme
        plist_data['readme'] = f"Alfred Workflow for {brand_config['shop_name']} Shopping"
        
        # Update notification title
        for obj in plist_data.get('objects', []):
            if obj.get('type') == 'alfred.workflow.output.notification':
                obj['config']['title'] = brand_config['shop_name']
        
        # Update script filter title and subtext
        for obj in plist_data.get('objects', []):
            if obj.get('type') == 'alfred.workflow.input.scriptfilter':
                obj['config']['title'] = f"{brand_config['shop_name']} Shopping"
                obj['config']['subtext'] = f"Go directly to your {brand_config['shop_name']} Shopping destination"
        
        # Write updated plist back to file
        with open(info_plist, 'wb') as f:
            plistlib.dump(plist_data, f)
    
    return brand_config

def get_logos(wf, stores):
    """Download store logos."""
    for store in stores:
        if 'logoUrls' in store and '_120x60' in store['logoUrls']:
            logo_url = store['logoUrls']['_120x60']
            logo_file = get_logo_file(wf, store)
            if not os.path.exists(logo_file):
                # Get brand config for referer
                brand_name = wf.stored_data('current_brand')
                brand_config = get_brand_config(brand_name)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                    'Referer': brand_config['url'] if brand_config else ''
                }
                try:
                    r = web.get(logo_url, headers=headers)
                    r.raise_for_status()
                    with open(logo_file, 'wb') as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Error downloading logo for {store['name']}: {e}")

def main(wf):
    """Main workflow function."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true', help='Update store data')
    parser.add_argument('--logos', action='store_true', help='Update store logos')
    parser.add_argument('--reinit', action='store_true', help='Reinitialize workflow')
    parser.add_argument('--brand', type=str, help='Set current brand')
    parser.add_argument('--favorite', type=str, help='Add or remove store from favorites')
    parser.add_argument('url', nargs='?', help='URL to open in browser')
    args = parser.parse_args()

    if args.url:
        # Open URL in browser using AppleScript
        script = f'open location "{args.url}"'
        run_applescript(script)
        return

    if args.update:
        stores = get_stores(force_update=True)
        if stores:
            wf.store_data('stores', stores)
            print("Store data updated successfully")
        else:
            print("Failed to update store data")
    elif args.logos:
        stores = get_stores(force_update=True)
        if stores:
            get_logos(wf, stores)
            print("Store logos updated successfully")
        else:
            print("Failed to update store logos")
    elif args.reinit:
        wf.clear_data()
        print("Workflow reinitialized")
    elif args.brand:
        try:
            brand_config = update_brand(wf, args.brand)
            print(f"Brand set to {brand_config['name']} ({brand_config['shop_name']})")
        except ValueError as e:
            print(f"Error: {e}")
    elif args.favorite:
        store = find_store_by_url(wf, args.favorite)
        if store:
            favorites = get_stored_data(wf, 'favorites') or []
            if store['id'] in favorites:
                favorites.remove(store['id'])
                print(f"{store['name']} removed from favorites")
            else:
                favorites.append(store['id'])
                print(f"{store['name']} added to favorites")
            wf.store_data('favorites', favorites)
        else:
            print("Could not find store")

if __name__ == u"__main__":
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-aadvantageshopping'
    })
    log = wf.logger
    sys.exit(wf.run(main))
    