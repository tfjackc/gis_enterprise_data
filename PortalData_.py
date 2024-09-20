import os, datetime, collections
from arcgis.gis import GIS
import pandas as pd

pd.set_option('display.max_colwidth', None)

# Portal Config
portal_URL = "https://domain.com/portal"
portal_uName = "username"
portal_pWord = "password"

# Output File Location
workDirectory = os.getcwd()


def scan_portal(portal_url, portal_username, portal_password):
    gis = GIS('{}'.format(portal_url), '{}'.format(portal_username), '{}'.format(portal_password))
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
                        a = collections.OrderedDict()
                        a['map_title'] = result.title
                        a['type'] = result.type
                        a['item_id'] = result.itemid
                        a['owner'] = result.owner
                        a['date_created'] = date_created
                        a['date_updated'] = date_updated
                        a['share_settings'] = result.access
                        a['content_status'] = result.content_status
                        a['total_storage'] = result.size
                        a['number_of_views'] = result.numViews
                        a['number_of_ratings'] = result.numRatings
                        a['average_rating'] = result.avgRating
                        a['layer_type'] = layer['layerType']
                        a['service_title'] = layer['title']
                        a['layer_url'] = layer['url']
                        about.append(a)

                    elif 'featureCollection' in layer:
                        for i in layer['featureCollection']['layers']:
                            layer_data = {
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
                                'layer_type': i['layerDefinition'].get('type', None),  # Access 'type' safely
                                'service_title': i['layerDefinition'].get('name', 'Unknown'),
                                'layer_url': i['layerDefinition'].get('name', 'Unknown') + ': No URL'
                            }
                            about.append(layer_data)

                    else:
                        if 'layers' in layer:
                            for more_info in layer['layers']:
                                layer_data = {
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
                                    'layer_type': more_info['layerType'],
                                    'service_title': more_info['title'],
                                    'layer_url': more_info['url']
                                }
                                about.append(layer_data)
    print("------complete------")
    dfwm = pd.DataFrame.from_dict(about)
    dfwm.to_csv(os.path.join(workDirectory, "portalWebMaps_Test.csv"))


if __name__ == '__main__':
    scan_portal(portal_URL, portal_uName, portal_pWord)