import requests
import xlsxwriter

# Global Variables
# API Credentials
headers = {
    'authUser': "KwikeeAPITestAccount",
    'authPwd': "$*n8#@J=Frg4=Qzs",
    'Ocp-Apim-Subscription-Key': "414de949421944f2a43fe549e5120a2a",
    'cache-control': "no-cache"
}

# Need to prompt user for input date, current date is a PLACEHOLDER
def get_gtin_list_updated_since(date):
    '''
    Return GTIN list from API based on how recently it has been updated.
    Requires a date input in form of YYYY-MM-DD.
    '''
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

def get_current_product_structure(gtin):
    '''
    Return json response in form of dictionary that contains asset Id, name, last modified date, brand, and image asset Ids.
    Requires gtin as input
    '''
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


def get_product_version_retrieve(asset_id):
    '''
    Return json response of product version.
    Requires asset id as input.
    '''
    url = "https://api.kwikee.com/manufacturer/qa/products/versions/3885971"
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    return data


def get_image_asset_retrieve(image_asset_id):
    '''
    Return json response of image asset data.
    Requires image asset id as input.
    '''
    url = "https://api.kwikee.com/manufacturer/qa/image-assets/3830176"
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    return data

def generateReport():
    '''
    Generate and populate excel report file
    '''
    workbook = xlsxwriter.Workbook('mfr_report.xlsx')
    return workbook

def generate_general_tab(workbook):
    '''
    Generate general tab headers to be populated with current product
    structure data
    Input: Excel workbook
    '''
    worksheet = workbook.add_worksheet('General Info')
    general_tab_headers = [
        'gtin',
        'name',
        'asset id',
        'last modified',
        'brand id',
        'permission group ids',
        'image asset id',
        'image last modified'
    ]
    worksheet.write_row(0, 0, general_tab_headers)
    workbook.close()

def populate_general_tab(workbook, gtin):
    for entry in gtin:
        data = get_current_product_structure(entry)


generate_general_tab(generateReport())


#test_gtin_list = get_gtin_list_updated_since(5)
#print(get_current_product_structure(test_gtin_list[0]))
#print(test_gtin_list)