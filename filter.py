# encoding: utf-8

import sys
import re
import argparse
from workflow.workflow import MATCH_ATOM, MATCH_STARTSWITH, MATCH_SUBSTRING, MATCH_ALL, MATCH_INITIALS, MATCH_CAPITALS, MATCH_INITIALS_STARTSWITH, MATCH_INITIALS_CONTAIN
from workflow import Workflow, ICON_WEB, ICON_WARNING, ICON_BURN, ICON_SWITCH, ICON_HOME, ICON_COLOR, ICON_INFO, ICON_SYNC, web, PasswordNotFound

log = None

def add_config_commands(wf, args, config_commands):
    word = args.query.lower().split(' ')[0] if args.query else ''
    config_command_list = wf.filter(word, config_commands.keys(), min_score=80, match_on=MATCH_SUBSTRING | MATCH_STARTSWITH | MATCH_ATOM)
    if config_command_list:
        for cmd in config_command_list:
            wf.add_item(config_commands[cmd]['title'],
                        config_commands[cmd]['subtitle'],
                        arg=config_commands[cmd]['args'],
                        autocomplete=config_commands[cmd]['autocomplete'],
                        icon=config_commands[cmd]['icon'],
                        valid=config_commands[cmd]['valid'])
    return config_command_list

def is_filtered_store(x, filters):
    filter_metadata = {':fav': 'isFavorite', ':prm': 'isElevation'}
    for key in filter_metadata:
        if key in filters:
            log.debug("active filter :"+key)
            value = filter_metadata[key]
            if 'isElevation' == value:
                p = x['rebate']
            else:
                p = x
            if value not in p or not p[value]:
                return False
    return True
    
def search_key_for_store(x):
    return x['name']
    
def get_subtitle(x):
    rebate = x['rebate']
    result = 'Earn '+str(rebate['value'])+' '+rebate['currency']
    if rebate['isElevation']:
        result = u'🏆 '+result+' : usually '+str(rebate['originalValue'])+' '+rebate['originalCurrency'] 
    if 'isFavorite' in x and x['isFavorite']:
        result = u'❤️ '+ result
    return result
        
def get_query_stores(wf, query, stores, filters):
    filtered_stores = filter(lambda x: is_filtered_store(x,filters), stores)
    result = wf.filter(query, filtered_stores, key=lambda x: search_key_for_store(x))
    # check to see if the first one is an exact match - if yes, remove all the other results
    if result and query and 'name' in result[0] and result[0]['name'] and result[0]['name'].lower() == query.lower():
        result = result[0:1]
    return result

def main(wf):
    # retrieve cached devices and scenes
    stores = wf.stored_data('stores')

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    log.debug("args are "+str(args))

    filters = [ t for t in args.query.split() if t.startswith(':') ]
    log.debug("filters are "+str(filters))
    # update query post extraction
    query = " ".join(filter(lambda x:x[0]!=':', args.query.split()))
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

    # Check for an update and if available add an item to results
    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
            'Action this item to install the update',
            autocomplete='workflow:update',
            icon=ICON_INFO)


    if not stores or len(stores) < 1:
        wf.add_item('No Stores...',
                    'Please use ae update - to update your AAdvantage Stores.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # If script was passed a query, use it to filter posts
    stores = get_query_stores(wf, query, stores, filters)

    if stores:
        # Loop through the returned devices and add an item for each to
        # the list of results for Alfred
        for store in stores:
            wf.add_item(title=store['name'],
                    subtitle=get_subtitle(store),
                    arg=store['clickUrl'],
                    autocomplete=store['name'],
                    valid=True,
                    icon='logos/'+str(store['id'])+'.jpg')
    else:
        wf.add_item(title='No qualifying stores...', 
                    subtitle="No stores matched your criteria", 
                    icon=ICON_WARNING)
    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-aadvantageshopping'
    })
    log = wf.logger
    sys.exit(wf.run(main))
    