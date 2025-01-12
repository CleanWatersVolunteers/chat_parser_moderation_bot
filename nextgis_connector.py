from datetime import datetime, timedelta
import requests
import json

ngw_host = 'https://blacksea-monitoring.nextgis.com'
auth = None

with open("__token_for_map.txt", "r") as f:
    u = f.readline()[:-1]
    p = f.readline()
    auth = (u, p)

NG_TEST = False

layer_match = {'oil':60, 'bird':100, "dead":147}

def add_point(lat, lon, comment, dtime, tg_link, layer_name, prio, region):
    assert(layer_name in layer_match.keys())
    feature = dict()
    feature['extensions'] = dict()
    feature['extensions']['attachment'] = None
    feature['extensions']['description'] = None
    feature['fields'] = dict()
    feature['fields']['lat'] = lat
    feature['fields']['lon'] = lon
    feature['fields']['comment'] = comment.replace("\n", ". ") + "\n" + tg_link
    feature['fields']['priority'] = prio
    #feature['fields']['count'] = count
    feature['fields']['region'] = region
    feature["source"] = "parser-bot"
    #feature['fields']['source'] = 
    print(tg_link)
    feature['geom'] = 'POINT (%s %s)' % (lon, lat)

    #t_dt = datetime.strptime(comment.split("\n")[0], "%Y-%m-%d %H:%M:%S")
    #date_export_format = datetime.strftime(t_dt, "%d.%m.%Y %H:%M:%S")
    feature['fields']['dt'] = (dtime + timedelta(hours=3)).isoformat()
    feature['fields']['dt_auto'] = datetime.now().isoformat()

    #create feature
    post_url = ngw_host + '/api/resource/' + str(layer_match[layer_name]) +'/feature/?srs=4326&dt_format=iso'
    print(feature, post_url)
    if NG_TEST == False:
        response = requests.post(post_url, data=json.dumps(feature), auth=auth)
        print(response)
        feature_id = response.json()['id']

        if response.status_code == 200:
            print("Feature created successfully:", response.json())
        else:
            print("Error creating feature:", response.status_code, response.text)

def get_history():
    #GET /api/resource/(int:id)/export?format=GPKG&srs=4326&zipped=True&fid=ngw_id&encoding=UTF-8
    #GET /api/resource/(int:id)/export?format=CSV&srs=4326&zipped=True&fid=ngw_id&encoding=UTF-8
    #GET /api/resource/(int:id)/csv
    get_url = ngw_host + '/api/resource/' + str(100) +'/geojson'
    
    print(get_url)
    response = requests.get(get_url, auth=auth)
    print(f"DATA: {response.json()}")

