import requests
from xml.dom import minidom

def retrieveLevel(levelId, is_design=False):
    URL = "http://www.fantasticcontraption.com/retrieveLevel.php"

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'id' : levelId}

    if is_design:
        PARAMS['loadDesign'] = '1'

    # sending POST request and saving the response as response object
    r = requests.post(URL, data = PARAMS)

    dom = minidom.parseString(r.text)

    return dom

def retrieveDesign(designId):
    return retrieveLevel(designId, is_design=True)