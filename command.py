# encoding: utf-8

from multiprocessing.sharedctypes import Value
import sys
import re
import argparse
from os.path import exists
from workflow.workflow import MATCH_ATOM, MATCH_STARTSWITH, MATCH_SUBSTRING, MATCH_ALL, MATCH_INITIALS, MATCH_CAPITALS, MATCH_INITIALS_STARTSWITH, MATCH_INITIALS_CONTAIN
from workflow import Workflow, ICON_WEB, ICON_NOTE, ICON_BURN, ICON_SWITCH, ICON_HOME, ICON_COLOR, ICON_INFO, ICON_SYNC, web, PasswordNotFound
from common import get_logo_file, get_stored_data

log = None

def get_stores():
    params = {
        'brand_id': 251,
        'app_key': '9ec260e91abc101aaec68280da6a5487',
        'app_id': '672b9fbb',
        'section_id': 10161,
        'limit': 2000,
        'sort_by': 'name',
        'fields': 'name,type,id,clickUrl,synonyms,showRebate,rebate,logoUrls._120x60,relatedActiveMerchants,categories',
        'include_inactive': 0
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://www.aadvantageeshopping.com',
        'Host': 'api.cartera.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'Referer': 'https://www.aadvantageeshopping.com/',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    r = web.get(url='https://api.cartera.com/content/v4/merchants', headers=headers, params=params)
    return r.json()['response']

def get_logos(wf, stores):
    for store in stores:
        filename = get_logo_file(wf, store)
        if not exists(filename):
            log.debug("Missing logo file - downloading "+filename)
            url = store['logoUrls']['_120x60']
            r = web.get(url)
            r.save_to_path(filename)

def main(wf):
    # retrieve cached devices and scenes
    stores = get_stored_data(wf, 'stores')
    favorites = get_stored_data(wf, 'favorites')
    
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --update argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--update', dest='update', action='store_true', default=False)
    parser.add_argument('--logos', dest='logos', action='store_true', default=False)
    # reinitialize 
    parser.add_argument('--reinit', dest='reinit', action='store_true', default=False)
    parser.add_argument('--favorite', dest='favorite', default='')
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    log.debug("args are "+str(args))

    words = args.query.split(' ') if args.query else []


    # Reinitialize if necessary
    if args.reinit:
        wf.reset()
        print('Workflow reinitialized')
        return 0

    # Update devices if that is passed in
    if args.update:  
        # update devices and scenes
        stores = get_stores()
        wf.store_data('stores', stores)
        print('Stores updated')
        return 0  # 0 means script exited cleanly
    
    # Update devices if that is passed in
    if args.logos:  
        get_logos(wf, stores)
        print('Logos updated')
        return 0  # 0 means script exited cleanly
    
    if args.favorite:
        stores = wf.stored_data('stores')
        url = args.favorite
        index = next((i for i, store in enumerate(stores) if store["clickUrl"] == url), None)
        if index is not None:
            currentState = favorites[stores[index]['id']] if stores[index]['id'] in favorites else False
            favorites[stores[index]['id']] = not currentState
        wf.store_data('favorites', favorites)
        prefix = ' un' if currentState else ' '
        print(stores[index]['name']+prefix+'set as favorite')

if __name__ == u"__main__":
    wf = Workflow(update_settings={
        'github_slug': 'schwark/alfred-aadvantageshopping'
    })
    log = wf.logger
    sys.exit(wf.run(main))
    