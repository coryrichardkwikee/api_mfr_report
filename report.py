import requests
import xlsxwriter

# Global Variables
# API Credentials
headers = {
    'authUser': "DiadeisAPIUser",
    'authPwd': "d*P7j(8)YL",
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
    querystring = {"updatedSince":"2019-04-01T00:00:00Z","page":"0"}
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
    url = "https://api.kwikee.com/manufacturer/qa/products/versions/{0}".format(asset_id)
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    return data


def get_image_asset_retrieve(image_asset_id):
    '''
    Return json response of image asset data.
    Requires image asset id as input.
    '''
    url = "https://api.kwikee.com/manufacturer/qa/image-assets/{0}".format(image_asset_id)
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    data = response.json()
    return data

def generate_report(gtin_list):
    '''
    Generate and populate excel report file
    Input: None
    Output: workbook
    '''
    workbook = xlsxwriter.Workbook('mfr_report.xlsx')
    worksheet = generate_general_tab(workbook)
    populate_general_tab(worksheet, gtin_list)
    worksheet = generate_image_tab(workbook)
    populate_image_tab(worksheet, gtin_list)
    worksheet = generate_version_tab(workbook)
    populate_version_tab(worksheet, gtin_list)
    workbook.close()


def generate_general_tab(workbook):
    '''
    Generate general tab headers to be populated with current product
    structure data
    Input: workbook
    Output: worksheet
    '''
    worksheet = workbook.add_worksheet('General Info')
    general_tab_headers = [
        'GTIN',
        'Asset Id',
        'Name',        
        'Brand Id',
        'Variants',
        'Last Modified',        
        'Permission Group Ids'
    ]
    worksheet.write_row(0, 0, general_tab_headers)
    return worksheet


def populate_general_tab(worksheet, gtin_list):
    '''
    Populates the general tab in an excel workbook, given
    a worksheet and a gtin list
    Input: worksheet, gtin_list
    Output: None
    '''
    # Begin populating with data after header row 
    row = 1
    col = 0
    for entry in gtin_list:
        permission_groups = ''
        variants = ''
        data = get_current_product_structure(entry)
        #convert permission groups to string
        for permission in data['permissionGroups']:
            permission_groups += permission + '; '
        '''
        #convert versions to string
        for version in data['versions']:
            versions += versions + '; '
        '''
        #convert variants to string
        for variant in data['variants']:
            variants += variants + '; '
        
        row_data = [
            entry,
            data['assetId'],
            data['name'],
            data['brand'],
            variants,
            data['lastModified'],
            permission_groups
        ]
        worksheet.write_row(row, col, row_data)
        row += 1


def generate_image_tab(workbook):
    '''
    Generates an empty tab for image data and some headers
    Input: Workbook
    Output: Worksheet
    '''
    worksheet = workbook.add_worksheet('Images')
    tab_headers = [
        'GTIN',
        'Asset Id',
        'Image Asset Id',
        'Image Last Modified',
        'Image Permission Groups',
        'Master Mimetype',
        'Master URL',
        'Master Modified Date'
    ]
    worksheet.write_row(0, 0, tab_headers)
    return worksheet


def populate_image_tab(worksheet, gtin_list):
    '''
    Populates the empty image tab in workbook
    Input: worksheet, gtin_list
    Output: None
    '''
    # set index under headers
    row = 1
    col = 0
    for gtin in gtin_list:
        data = get_current_product_structure(gtin)
        # test if gtin contains image data
        try: 
            x = data['images']
            # print('data contains images')
        except:
            print('{0} does not contain images'.format(gtin))
            continue
        # Iterate over returned image assets and add image data to excel
        for image in data['images']:
            # query for image asset data
            image_data = get_image_asset_retrieve(image['assetId'])
            # convert image permission groups to string
            permission_groups = ""
            for permission in image['permissionGroups']:
                permission_groups += permission + '; '
            # pull out master image data
            master_image_dict = find_master_image(image_data)
            #print("master image dict is {0}".format(master_image_dict))
            if master_image_dict == None:
                continue
            if isinstance(master_image_dict['modifiedDate'], dict):
               master_image_dict['modifiedDate'] = None         
            # Construct row of data to be added for each image entry
            row_data = [
                gtin,
                data['assetId'],
                image['assetId'],
                image['lastModified'],
                permission_groups,
                master_image_dict['mimetype'],
                master_image_dict['url'],
                master_image_dict['modifiedDate']
                ]
            worksheet.write_row(row, col, row_data)
            # Insert next row below current row
            row += 1


def find_master_image(json_image_data):
    '''
    Scans json response from Image Asset - Retrieve call
    for master image. Returns none if none.
    Input: json dictionary
    Output: master image dictionary
    ''' 
    # Throws error if image data not filled out. 
    try:   
        for file in json_image_data['responseData']['files']:
            if file['key'] == 'master':
                return file
        return None
    except:
        return None


def generate_version_tab(workbook):
    '''Generates empty verion tab in workbook
    Input: workbook
    Output: worksheet
    '''
    worksheet = workbook.add_worksheet('Versions')
    tab_headers = [
        'GTIN',
        'Version Asset Id',
        'Version Permission Group Ids',
        'Last Modified'
    ]
    worksheet.write_row(0, 0, tab_headers)
    return worksheet


def populate_version_tab(worksheet, gtin_list):
    '''Populates the version tab of report
    Input: worksheet, gtin_list
    Output: None
    '''
    # set row index after headers
    row = 1
    col = 0
    for gtin in gtin_list:
        # get product structure data
        data = get_current_product_structure(gtin)
        # parse primary version Id
        # convert permissions group to string
        permissions = ""
        for permission in data['permissionGroups']:
            permissions += '{0}; '.format(permission)
        row_data = [
            gtin,
            data['assetId'],
            permissions,
            data['lastModified']
        ]
        worksheet.write_row(row, col, row_data)
        row += 1
        # parse remaining versions
        for version in data['versions']:
            permissions = ''
            for permission in version['permissionGroups']:
                permissions += '{0}; '.format(permission)
            row_data = [
                gtin,
                version['assetId'],
                permissions,
                version['lastModified']
            ]
            worksheet.write_row(row, col, row_data)
            row += 1


test_gtin_list = get_gtin_list_updated_since(5)
generate_report(test_gtin_list)