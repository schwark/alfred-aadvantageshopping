# encoding: utf-8

import datetime
import sys
import argparse
from workflow import (
    Workflow, ICON_WEB, ICON_NOTE, ICON_INFO, ICON_BURN, ICON_SYNC, web, PasswordNotFound
)
from workflow.background import is_running, run_in_background
from common import get_buttons, save_button, delete_button, get_icon, get_logo_file, get_stored_data

log = None

def add_config_commands(wf, args, config_commands):
    """Add configuration commands to workflow items."""
    word = args.query.lower().split(' ')[0] if args.query else ''
    config_command_list = wf.filter(word, config_commands.keys(), min_score=80)
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
    spacer = u'   '
    rebate = x['rebate']
    regularly = ''
    result = u'earn '+str(rebate['value'])+' '+rebate['currency']
    if rebate['isElevation']:
        bonus_pct = get_bonus_percentage(x)
        result = u'🏆 '+result+f' (+{bonus_pct:.0f}% bonus)'
        regularly = u' ↓ regularly '+str(rebate['originalValue'])+' '+rebate['originalCurrency'] 
    if x['id'] in favorites and favorites[x['id']]:
        result = u'❤️ '+ result
    result += spacer+regularly
    categories = get_categories(x)
    if categories:
        #result = u'{0:<70} {1:<50}'.format(result, u' ⦿ '+categories) 
        #result = result + spacer + u'⦿ '+categories
        pass
    return result
        
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

def get_query_stores(wf, query, stores, filters, favorites):
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
    favorites = get_stored_data(wf, 'favorites')

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    log.debug("args are "+str(args))

    filters = [ t for t in args.query.split() ] if args.query else []
    filters = [ t for t in filters if t.startswith(':') ]
    log.debug("filters are "+str(filters))
    # update query post extraction
    query = " ".join(filter(lambda x:x[0]!=':', args.query.split())) if args.query else ""
    log.debug("query is now "+query)

    config_commands = {
        'update': {
            'title': 'Update Stores',
            'subtitle': 'Update the supported stores on AAdvantage',
            'autocomplete': 'update',
            'args': ' --update',
            'icon': ICON_SYNC,
            'valid': True
        },
        'logos': {
            'title': 'Update Store Logos',
            'subtitle': 'Update the supported store logos on AAdvantage',
            'autocomplete': 'logos',
            'args': ' --logos',
            'icon': ICON_SYNC,
            'valid': True
        },
        'reinit': {
            'title': 'Reinitialize the workflow',
            'subtitle': 'CAUTION: this deletes all scenes, devices and apikeys...',
            'autocomplete': 'reinit',
            'args': ' --reinit',
            'icon': ICON_BURN,
            'valid': True
        },
        'workflow:update': {
            'title': 'Update the workflow',
            'subtitle': 'Updates workflow to latest github version',
            'autocomplete': 'workflow:update',
            'args': '',
            'icon': ICON_SYNC,
            'valid': True
        }
    }

    # add config commands to filter
    add_config_commands(wf, args, config_commands)

    ####################################################################
    # View/filter devices or scenes
    ####################################################################

    freq = 86400
    # Is cache over 1 hour old or non-existent?
    if datetime.datetime.now() - datetime.datetime.fromtimestamp(last_update) > datetime.timedelta(seconds=freq):
        run_in_background('update',
                        ['/usr/bin/python3',
                        wf.workflowfile('command.py'),
                        '--update'])

    # Check for an update and if available add an item to results
    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
            'Action this item to install the update',
            autocomplete='workflow:update',
            icon=ICON_INFO)

    if is_running('update'):
        # Tell Alfred to run the script again every 0.5 seconds
        # until the `update` job is complete (and Alfred is
        # showing results based on the newly-retrieved data)
        wf.rerun = 0.5
        # Add a notification if the script is running
        wf.add_item('Updating stores...', icon=ICON_INFO)

    if not stores or len(stores) < 1:
        wf.add_item('No Stores...',
                    'Please use ae update - to update your AAdvantage Stores.',
                    valid=False,
                    icon=ICON_NOTE)
        wf.send_feedback()
        return 0

    # If script was passed a query, use it to filter posts
    stores = get_query_stores(wf, query, stores, filters, favorites)

    if stores:
        # Loop through the returned devices and add an item for each to
        # the list of results for Alfred
        for store in stores:
            wf.add_item(title=store['name'],
                    subtitle=get_subtitle(store, favorites),
                    arg=store['clickUrl'],
                    autocomplete=store['name'],
                    valid=True,
                    icon=get_logo_file(wf, store))
    else:
        wf.add_item(title='No qualifying stores...', 
                    subtitle="No stores matched your criteria", 
                    icon=ICON_NOTE)
    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0

if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-aadvantageshopping'
    })
    log = wf.logger
    sys.exit(wf.run(main))
    