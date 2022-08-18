def get_logo_file(wf, store):
    filename = wf.datafile(str(store['id'])+'.jpg')
    return filename

def get_stored_data(wf, name):
    data = {}
    try:
        data = wf.stored_data(name)
    except ValueError:
        pass
    return data

