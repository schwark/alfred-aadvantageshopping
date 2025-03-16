# encoding: utf-8

import os
import json
from workflow import ICON_WEB

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

