import os
import datetime
import collections
import pandas as pd
from arcgis.gis import GIS

pd.set_option('display.max_colwidth', None)

# Portal Config
portal_URL = "https://domain.com/portal"
portal_uName = "username"
portal_pWord = "password"

# Output File Location
work_directory = os.getcwd()


def append_layer_data(about, result, date_created, date_updated, layer_type, service_title, layer_url):
    about.append({
        'map_title': result.title,
        'type': result.type,
        'item_id': result.itemid,
        'owner': result.owner,
        'date_created': date_created,
        'date_updated': date_updated,
        'share_settings': result.access,
        'content_status': result.content_status,
        'total_storage': result.size,
        'number_of_views': result.numViews,
        'number_of_ratings': result.numRatings,
        'average_rating': result.avgRating,
        'layer_type': layer_type,
        'service_title': service_title,
        'layer_url': layer_url
    })


def scan_portal(portal_url, portal_username, portal_password):
    gis = GIS(f"{portal_url}", f"{portal_username}", f"{portal_password}")
    search_results = gis.content.search(query='', item_type='Web Map', max_items=10000)
    about = []
    print("------scanning portal------")

    for result in search_results:
        data = result.get_data()
        date_created = datetime.datetime.fromtimestamp(result.created / 1000).strftime("%m/%d/%Y %I:%M:%S %p")
        date_updated = datetime.datetime.fromtimestamp(result.modified / 1000).strftime("%m/%d/%Y %I:%M:%S %p")

        if 'operationalLayers' in data:
            operational_layers = data['operationalLayers']
            for layer in operational_layers:
                if layer['layerType'] != "ArcGISTiledImageServiceLayer":
                    if 'url' in layer:
                        append_layer_data(about, result, date_created, date_updated, 
                                          layer['layerType'], layer['title'], layer['url'])

                    elif 'featureCollection' in layer:
                        for i in layer['featureCollection']['layers']:
                            append_layer_data(about, result, date_created, date_updated,
                                              i['layerDefinition'].get('type', 'Unknown'),
                                              i['layerDefinition'].get('name', 'Unknown'),
                                              f"{i['layerDefinition'].get('name', 'Unknown')}: No URL")

                    else:
                        if 'layers' in layer:
                            for more_info in layer['layers']:
                                append_layer_data(about, result, date_created, date_updated,
                                                  more_info['layerType'], more_info['title'], more_info['url'])

    print("------complete------")
    dfwm = pd.DataFrame.from_dict(about)
    dfwm.to_csv(os.path.join(work_directory, "portalWebMaps_Test.csv"))


if __name__ == '__main__':
    scan_portal(portal_URL, portal_uName, portal_pWord)
