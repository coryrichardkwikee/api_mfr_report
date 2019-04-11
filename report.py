import requests

# Global Variables
# API Credentials
headers = {
    'authUser': "KwikeeAPITestAccount",
    'authPwd': "$*n8#@J=Frg4=Qzs",
    'Ocp-Apim-Subscription-Key': "414de949421944f2a43fe549e5120a2a",
    'cache-control': "no-cache"
    }

# Return GTIN list from API based on how recent it has been updated
# Need to prompt user for input date, current date is a PLACEHOLDER
def getGTINListUpdatedSince(date):
    # Need to convert date to UTC from CST
    url = "https://api.kwikee.com/manufacturer/qa/products"
    querystring = {"updatedSince":"2019-04-05T00:00:00Z","page":"0"}
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    data = response.json()
    try: 
        gtin_List = data['gtin']
        return gtin_List
    except:
        print "No products updated since {0}".format(date)
        return None

# Return json response in form of dictionary that contains assetId, name, last modified, brand, and all image asset Ids
def getCurrentProductStructure(gtin):
    url = "https://api.kwikee.com/manufacturer/qa/entities/gtin/{0}".format(gtin)
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    try:
        status = data['status']
        print "No products match gtin, {0}".format(gtin)
        return None
    except:
        return data

testGTINList = getGTINListUpdatedSince(5)
#print(getCurrentProductStructure(testGTINList[0]))
print(testGTINList)