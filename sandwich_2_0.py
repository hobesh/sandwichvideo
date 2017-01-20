#v2.0

print "Sandwich V2.0 loaded..."

import requests, json, datetime
from fuzzwuzzy import process

class Client:
    def __init__(self, record):
        self.name = record["fields"]["Name"]
        try:
            self.website = record["fields"]["Website"]
        except KeyError:
            self.website = False
        self.projects = []
        try:
            self.projects = record["fields"]["Projects"]
        except:
            pass
        self.endpoint = record["id"]
        
    def __str__(self):
        if self.website:
            return "%s (%s)" %(self.name, self.website)
        else:
            return "%s" %(self.name)

class Project:
    def __init__(self, record):
        self.name = record["fields"]["Project"]
        self.year = record["fields"]["Year"]
        self.endpoint = record["id"]
    def __str__(self):
        if self.website:
            return "%s (%s)" %(self.name, self.year)
        else:
            return "%s" %(self.name)
            
            
def get_auth(csv_path):
    f = open(csv_path, "r")
    lines =  f.read().split('\n')
    f.close()
    authy = {}
    for l in lines:
        line_chunks = l.split(',')
        service = line_chunks[0]
        line_chunks.pop(0)
        service_dict = {}
        for chunk in line_chunks:
            key,sep,token = chunk.rstrip('\r').partition("=")
            service_dict[key] = token
        authy[service] = service_dict
    return authy 
    
authy = get_auth('/Volumes/Sandwich/assets/python/auth.csv')
api_key = authy['airtable sandwich projects']['api_key']
shots_api_key = authy['airtable sandwich shots']['api_key']
atProjects = authy['airtable sandwich projects']['api_url']
atVideos = authy['airtable sandwich videos']['api_url']
atClients = authy['airtable sandwich clients']['api_url']
atShots = ['airtable sandwich shots']['api_url']



def createProject(projectName):
    api_url = atProjects
    now = datetime.datetime.now()
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    data = '{"fields": {"Project":"%s", "Year":%d, "Status":"Creative"}}' %(projectName,int(now.year))
    r = requests.post(api_url, headers=headers, data=data)
    created_proj = Project(json.loads(r.text))
    if r.status_code == 200:
        print "%s added to database." %(created_proj.name)
        return created_proj
    else: 
        return False
    
def createClient(clientName):
    api_url = atClients
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    data = {"fields": {"Name": clientName}}
    data = json.dumps(data,separators=(',',':'))
    r = requests.post(api_url, headers=headers, data=data)
    created_client = Client(json.loads(r.text))
    if r.status_code == 200:
        print "%s added to database." %(created_client.name)
        return created_client
    else: 
        return False
        
def updateRecord(table_url, endpoint, data):
    api_url = table_url + "/" + endpoint
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    r = requests.patch(api_url, headers=headers, data=data)
    json_data = json.loads(r.text)
    if r.status_code == 200:
        return json_data
    else: 
        return False

def get_record_endpoints(table_url, view, keyname="Name"):
    params = {"api_key": api_key, "view": view }
    
    r = requests.get(table_url, params)
    json_data = json.loads(r.text)
    records_array = json_data["records"]
    
    endpoint_dict = {}
    for record in records_array:
        record_endpoint = record["id"]
        recordinfo_dict = record["fields"]
        endpoint_dict[recordinfo_dict[keyname]] = record_endpoint
        
    return endpoint_dict
    
def get_video_record_endpoints(view):
    fields = ["Name","Latest Cut"]
    params = {"api_key": api_key, "view": view }

    r = requests.get(atVideos,params)
    json_data = json.loads(r.text)
    records_array = json_data["records"]
    
    video_endpoint_dict = {}
    for video in records_array:
        record_endpoint = video["id"]
        projectinfo_dict = video["fields"]
        video_endpoint_dict[projectinfo_dict["Name"]] = record_endpoint
        
    return video_endpoint_dict

def get_shot_record_endpoints(view):
    fields = ["Name"]
    params = {"api_key": api_key, "view": view}

    r = requests.get(atShots, params)
    json_data = json.loads(r.text)
    records_array = json_data["records"]

    record_endpoint_dict = {}
    for project in records_array:
        record_endpoint = project["id"]
        projectinfo_dict = project["fields"]
        record_endpoint_dict[projectinfo_dict["Name"]] = record_endpoint
    return record_endpoint_dict

def updateLatestcut(video,cut):
    record_endpoints = get_video_record_endpoints("Sandwich Editorial")
    api_url = atVideos + "/" + record_endpoints[video]
    data = '{"fields": {"Latest Cut":"' + cut + '"}}'
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    r = requests.patch(api_url, headers=headers, data=data)
    json_data = json.loads(r.text)
    if r.status_code == 200:
        return "Thanks for adding a cut."
    else: 
        return "ERROR " + str(r.status_code)

def get_ss_time(air_video):
    records_list = getViewRecords(atVideos,"Sandwich Editorial",["Name","Screenshot Offset"])
    return_value = False
    for r in records_list:
        try:
            if str(r["fields"]["Name"]) == str(air_video):
                return_value = r["fields"]["Screenshot Offset"]
        except KeyError:
            pass
    
    return return_value

def update_airtable_screenshot(screenshot_url,air_video):
    print "This is the video we've matched to add the screenshot: " +air_video
    record_endpoints = get_video_record_endpoints("Sandwich Editorial")
    api_url = atVideos + "/" + record_endpoints[air_video]
    data = '{"fields": {"Screenshot": [{"url":"' + screenshot_url + '"}]}}'
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    r = requests.patch(api_url, headers=headers, data=data)
    json_data = json.loads(r.text)
    if r.status_code == 200:
        return "Thanks for adding a Screenshot."
    else: 
        return "ERROR " + str(r.status_code)

def update_shot_screenshot(screenshot_url,shot):
    print "This is the shot we've matched to for that screenshot: " +shot
    record_endpoints = get_shot_record_endpoints("All Shots")
    api_url = atShots + "/" + record_endpoints[shot]
    data = '{"fields": {"Screenshot": [{"url":"' + screenshot_url + '"}]}}'
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
    r = requests.patch(api_url, headers=headers, data=data)
    json_data = json.loads(r.text)
    if r.status_code == 200:
        return "Thanks for adding a Screenshot."
    else:
        return "ERROR " + str(r.status_code)

def update_shot(path, db_link):
    # pass the path + db link to this function to update that shot in airtable
    record_endpoints = get_shot_record_endpoints("Working Shots")
    path_chunks = path.split("/")
    for key in record_endpoints:
        results = process.extract(key, path_chunks)
        match, score = results[0]
        if score == 100:
            # ask airtable for record
            matched_shot = key
            api_url = atShots + "/" + record_endpoints[key]
            print "Got a match.  Breaking..."
            break

    data = '{"fields": {"Latest Comp":"' + path + '","Dropbox Link":"' + db_link + '","Status": "Ready To Review"}}'
    headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}

    try:
        r = requests.patch(api_url, headers=headers, data=data)
        json_data = json.loads(r.text)
        return matched_shot
    except:
        return False

def updateLatestcut2(video,cut):
    record_endpoints = get_video_record_endpoints("Sandwich Editorial")
    data = {"fields": {"Latest Cut": cut}}
    data = json.dumps(data,separators=(',',':'))
    created_video = updateRecord(atVideos, record_endpoints[video], data)
    return created_video
    
def getAllRecords(table_url, custom_fields):
    if len(custom_fields) <= 1:
        print "ERROR: You must pass at least 2 fields in the custom_fields parameter"
        record_List = []
    else:
        api_url = table_url
        record_List = []
        headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
        data = {"fields": custom_fields}
        offset = False
        runs = 1
        while 1:
            if offset:
                data["offset"] = offset
            r = requests.get(api_url, headers=headers, params=data)
            if r.status_code == 200:
                pass
            else: 
                print "ERROR " + str(r.status_code)
                print r.text
            json_data = json.loads(r.text)
            for client in json_data["records"]:
                record_List.append(client)
            if "offset" in json_data:
                runs = runs + 1
                offset = json_data["offset"]
            else:
                print "Record list finished after %d runs. %d total records added." %(runs,len(record_List))
                break
    
    return record_List

def getViewRecords(table_url, view, custom_fields):
    if len(custom_fields) <= 1:
        print "ERROR: You must pass at least 2 fields in the custom_fields parameter"
        record_List = []
    else:
        api_url = table_url
        record_List = []
        headers = {'Authorization': 'Bearer ' + api_key, "Content-type": "application/json"}
        data = {"view": view, "fields": custom_fields}
        offset = False
        runs = 1
        while 1:
            if offset:
                data["offset"] = offset
            r = requests.get(api_url, headers=headers, params=data)
            if r.status_code == 200:
                pass
            else: 
                print "ERROR " + str(r.status_code)
                print r.text
            json_data = json.loads(r.text)
            for client in json_data["records"]:
                record_List.append(client)
            if "offset" in json_data:
                runs = runs + 1
                offset = json_data["offset"]
            else:
                print "Record list finished after %d runs. %d total records added." %(runs,len(record_List))
                break
    
    return record_List

    
