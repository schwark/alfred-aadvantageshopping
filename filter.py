# encoding: utf-8

import datetime
import sys
import argparse
import os
from workflow import (
    Workflow, ICON_WEB, ICON_NOTE, ICON_BURN, ICON_SYNC
)
from common import get_logo_file, get_stored_data, get_stores
from brands import BRANDS
from command import update_brand

log = None

# Configuration commands for the workflow
config_commands = {
    'reinit': {
        'title': 'Reinitialize workflow',
        'subtitle': 'Reset all settings to defaults',
        'args': '--reinit',
        'autocomplete': 'reinit',
        'icon': ICON_BURN,
        'valid': True
    },
    'update': {
        'title': 'Update stores',
        'subtitle': 'Update the list of stores',
        'args': '--update',
        'autocomplete': 'update',
        'icon': ICON_SYNC,
        'valid': True
    },
    'logos': {
        'title': 'Update logos',
        'subtitle': 'Update store logos',
        'args': '--logos',
        'autocomplete': 'logos',
        'icon': ICON_SYNC,
        'valid': True
    },
    'brand': {
        'title': 'Change brand',
        'subtitle': 'Switch between different brands',
        'args': '--brand',
        'autocomplete': 'brand ',
        'icon': ICON_WEB,
        'valid': False
    }
}

def add_config_commands(wf, args, config_commands):
    """Add configuration commands to workflow items."""
    if not args.query:
        return []
        
    words = args.query.lower().split()
    if not words:
        return []
        
    command = words[0]
    
    # Handle brand command specially
    if command == 'brand':
        brand_query = words[1] if len(words) > 1 else ''
        # Filter brands based on query
        matching_brands = wf.filter(brand_query, BRANDS.keys(), min_score=80)
        current_brand = get_stored_data(wf, 'current_brand')
        if isinstance(current_brand, bytes):
            current_brand = current_brand.decode('utf-8')
            
        for brand_key in matching_brands:
            brand_info = BRANDS[brand_key]
            subtitle = f"Set {brand_info['name']} as current brand"
            if brand_key == current_brand:
                subtitle = f"✓ {subtitle}"
            wf.add_item(
                title=brand_info['name'],
                subtitle=subtitle,
                arg=f"--brand {brand_key}",
                autocomplete=f"brand {brand_key}",
                icon=brand_info['favicon'],
                valid=True
            )
        return matching_brands
    
    # Handle other commands
    config_command_list = wf.filter(command, config_commands.keys(), min_score=80)
    if config_command_list:
        for cmd in config_command_list:
            wf.add_item(config_commands[cmd]['title'],
                       config_commands[cmd]['subtitle'],
                       arg=config_commands[cmd]['args'],
                       autocomplete=config_commands[cmd]['autocomplete'],
                       icon=config_commands[cmd]['icon'],
                       valid=config_commands[cmd]['valid'])
    return config_command_list

def parse_add_command(query):
    """Parse add command in format: add name|url|tag1,tag2."""
    parts = query.split('|')
    if len(parts) < 2:
        return None
    
    name = parts[0].strip()
    url = parts[1].strip()
    tags = parts[2].strip().split(',') if len(parts) > 2 else []
    
    return {'name': name, 'url': url, 'tags': tags}

def is_filtered_store(x, filters, favorites):
    if ':fav' in filters and favorites and x['id'] not in favorites:
        return False
    if ':prm' in filters and not x['rebate']['isElevation']:
        return False
    return True

def get_categories(x):
    categories = [c['name'] for c in (x['categories'] if 'categories' in x else [])]
    return (', '.join(categories)) if categories else ''
    
def search_key_for_store(x):
    categories = get_categories(x)
    return x['name']+(' '+categories if categories else '')

def get_subtitle(x, favorites):
    """Get subtitle for store item."""
    subtitle = []
    
    # Add favorite indicator
    if x['id'] in favorites:
        subtitle.append('❤️')
    
    # Add rebate information
    rebate = x['rebate']
    if rebate['isElevation']:
        bonus_pct = get_bonus_percentage(x)
        subtitle.append(f"⚡ {rebate['value']} {rebate['currency']} (+{bonus_pct:.0f}% bonus)")
    else:
        subtitle.append(f"💰 {rebate['value']} {rebate['currency']}")
    
    # Add categories if available
    if 'categories' in x and x['categories']:
        categories = [cat['name'] for cat in x['categories']]
        subtitle.append(f"🏷️ {', '.join(categories)}")
    
    # Add direct indicator if applicable
    if x.get('isDirect', False):
        subtitle.append("🎯 Direct")
    
    # Add mobile tracking indicator if applicable
    if x.get('flags', {}).get('tracksMobile', False):
        subtitle.append("📱 Mobile")
    
    return '  '.join(subtitle)
        
def get_bonus_percentage(store):
    """Get the pre-calculated bonus percentage for a store."""
    return store.get('bonus_percentage', 0)

def get_query_stores(wf, query, stores, filters, favorites):
    if stores is None:
        wf.logger.error("No stores available")
        return []
        
    filtered_stores = list(filter(lambda x: is_filtered_store(x,filters,favorites), stores))
    
    # If :prm filter is present, sort by bonus percentage in descending order
    if ':prm' in filters:
        # First filter to only promotional stores
        promo_stores = [store for store in filtered_stores if store['rebate']['isElevation']]
        # Sort by bonus percentage
        promo_stores.sort(
            key=get_bonus_percentage,
            reverse=True
        )
        return promo_stores
    
    # Otherwise use normal filtering
    result = wf.filter(query, filtered_stores, key=lambda x: search_key_for_store(x))
    # check to see if the first one is an exact match - if yes, remove all the other results
    if result and query and 'name' in result[0] and result[0]['name'] and result[0]['name'].lower() == query.lower():
        result = result[0:1]
    return result

def main(wf):
    # retrieve cached devices and scenes
    last_update = get_stored_data(wf, 'last_update') or 0
    if isinstance(last_update, datetime.datetime):
        last_update = int(last_update.timestamp())
    stores = get_stored_data(wf, 'stores')
    favorites = get_stored_data(wf, 'favorites') or {}
    
    # Ensure default brand is set and icon.png exists
    current_brand = get_stored_data(wf, 'current_brand')
    if not current_brand:
        current_brand = 'american'.encode('utf-8')
        wf.store_data('current_brand', current_brand)
    
    # Check and update brand if icon.png is missing
    if isinstance(current_brand, bytes):
        current_brand = current_brand.decode('utf-8')
    dst_icon = wf.workflowfile('icon.png')
    if not os.path.exists(dst_icon):
        try:
            update_brand(wf, current_brand)
        except ValueError as e:
            log.error(f"Error updating brand: {e}")
    
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    log.debug("args are "+str(args))

    # Add config commands
    add_config_commands(wf, args, config_commands)
    
    # Get stores for current brand
    stores = get_stores()
    
    # Extract filters and update query
    filters = [t for t in args.query.split()] if args.query else []
    filters = [t for t in filters if t.startswith(':')]
    query = " ".join(filter(lambda x: x[0]!=':', args.query.split())) if args.query else ""
    
    # Get filtered stores
    filtered_stores = get_query_stores(wf, query, stores, filters, favorites)
    
    # Add filtered stores to results
    for store in filtered_stores:
        wf.add_item(
            title=store['name'],
            subtitle=get_subtitle(store, favorites),
            arg=f'"{store["clickUrl"]}"',  # Quote the URL
            valid=True,
            icon=get_logo_file(wf, store)
        )
    
    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-aadvantageshopping'
    })
    log = wf.logger
    sys.exit(wf.run(main))
    