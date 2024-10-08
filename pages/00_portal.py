import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import solara
import solara.lab
import random

# access data from csv...
dfwm = pd.read_csv("data/portalWebMaps_Test.csv")
dfsolo = pd.read_csv("data/solo_layers.csv")
dfwm['storage'] = np.where(dfwm['layer_url'].str.contains('Hosted'), 'Hosted', 'Referenced')
dfsubset = dfwm[['map_title', 'item_id', 'service_title', 'layer_url', 'share_settings', 'number_of_views', 'storage']]
dfsubset_san = dfsubset.sort_values(by=['number_of_views'], ascending=False)
dfsubset_san['layer_url'] = dfsubset_san['layer_url'].str.replace(r'^.*services/([^/]*)/.*$', r'\1', regex=True)

int_value = solara.reactive(30)
iter_slider = solara.reactive(50)

map_titles = dfsubset_san['map_title'].unique()
webMaps = []
map_title_to_color = {}
mttc = {}
for title in map_titles:
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    color = f'rgba({red},{green},{blue},0.55)'
    map_title_to_color[title] = color
    webMaps.append(title)

dfsubset_san['colors'] = [map_title_to_color[title] for title in dfsubset_san['map_title']]
dfsubset_san['map_color'] = 'rgba(54,214,172,0.8)'
dfsubset_san['service_color'] = 'rgba(99,110,250,0.8)'

dfcolors = pd.DataFrame()
dfcolors[['item', 'colors']] = dfsubset_san[['map_title', 'map_color']]
dfcolors = pd.concat([dfcolors, dfsubset_san[['layer_url', 'service_color']].rename(columns={'layer_url': 'item', 'service_color': 'colors'})], ignore_index=True)


def datavalues(value):
    dfsubset_san['quant_views'] = (((dfsubset_san['number_of_views'] / 250000) * 80) + value)
    updateplot(dfsubset_san)


def updateplot(dfsubset_san):
    map_titles = dfsubset_san['map_title'].unique()
    webMaps = []
    for title in map_titles:
        webMaps.append(title)

    dfsubset_san['map_color'] = 'rgba(54,214,172,0.9)'
    dfsubset_san['service_color'] = 'rgba(99,110,250,0.9)'

    G = nx.Graph()
    G = nx.from_pandas_edgelist(dfsubset_san, 'map_title', 'service_title')
    pos = nx.spring_layout(G)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#000000'),
        hoverinfo='none',
        mode='lines',
    )

    node_x = []
    node_y = []
    node_text = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_info = str(node) + "<br># of connections: " + str(len(list(G.neighbors(node))))
        node_text.append(node_info)
        if node in dfsubset_san['map_title'].values:
            node_color.append(dfsubset_san.loc[dfsubset_san['map_title'] == node, 'map_color'].iloc[0])
        else:
            node_color.append(dfsubset_san.loc[dfsubset_san['service_title'] == node, 'service_color'].iloc[0])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_text,
        hoverinfo='text',
        mode='markers+text',
        marker=dict(
            size=dfsubset_san['quant_views'],
            color=node_color
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=975
    ))

    return solara.FigurePlotly(fig)


nodes = []
links = []


def add_node(node_name):
    if node_name not in nodes:
        nodes.append(node_name)


def add_link(source, target, value, views, color):
    add_node(source)
    add_node(target)
    add_node(views)
    links.append({"source": nodes.index(source), "target": nodes.index(target), "views": nodes.index(views), "color": color, 'value': value})


for item in zip(dfsubset_san['map_title'], dfsubset_san['layer_url'], dfsubset_san['number_of_views'], dfsubset_san['service_title'], dfsubset_san['colors']):
    source = f"{item[0]}"
    target = f"{item[1]}: {item[3]}"
    value = 1
    color = f"{item[4]}"
    views = f"{item[2]}"
    add_link(source, target, value, views, color)
    add_link(target, views, value, views, color)

sankey_trace = go.Sankey(
    arrangement="freeform",
    node=dict(
        pad=30,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=nodes,
        color=[link["color"] for link in links]

    ),
    link=dict(
        source=[link["source"] for link in links],
        target=[link["target"] for link in links],
        value=[link["value"] for link in links],
        color=[link["color"] for link in links]
    )
)

sanfig = go.Figure(data=[sankey_trace])

sanfig.update_layout(title_text="Web Maps Connections to Layers in Portal",
                     font_size=18,
                     height=6000)

map_titles = dfsolo['map_title'].unique()
webMaps = []
map_title_to_color = {}
mttc = {}
for title in map_titles:
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    color = f'rgba({red},{green},{blue},0.55)'
    map_title_to_color[title] = color
    webMaps.append(title)

dfsolo['colors'] = [map_title_to_color[title] for title in dfsolo['map_title']]
dfsolo['map_color'] = 'rgba(54,214,172,0.8)'
dfsolo['service_color'] = 'rgba(99,110,250,0.8)'

dfcolors = pd.DataFrame()
dfcolors[['item', 'colors']] = dfsolo[['map_title', 'map_color']]
dfcolors = pd.concat([dfcolors, dfsolo[['layer_url', 'service_color']].rename(columns={'layer_url': 'item', 'service_color': 'colors'})], ignore_index=True)


nodes = []
links = []
for item in zip(dfsolo['map_title'], dfsolo['layer_url'], dfsolo['number_of_views'], dfsolo['service_title'], dfsolo['colors'], dfsolo['service_layers']):
    source = f"{item[5]}"
    target = f"{item[0]}"
    value = 1
    color = f"{item[4]}"
    views = f"{item[2]}"
    add_link(source, target, value, views, color)

sankey_solo = go.Sankey(
    arrangement="freeform",
    node=dict(
        pad=30,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=nodes,
        color=[link["color"] for link in links]

    ),
    link=dict(
        source=[link["source"] for link in links],
        target=[link["target"] for link in links],
        value=[link["value"] for link in links],
        color=[link["color"] for link in links]
    )
)

sanfig_solo = go.Figure(data=[sankey_solo])

sanfig_solo.update_layout(
    title_text="Layer Connections to Web Maps in Portal",
    font_size=18,
    height=6000
)

@solara.component
def Page():
    with solara.Column() as main:
        with solara.AppBarTitle():
            solara.Text("Crook County GIS Portal Map")

        with solara.lab.Tabs(background_color="#084685", dark=True):

            with solara.lab.Tab("Sankey Layout", icon_name="mdi-chart-line"):
                with solara.Card():

                    solara.FigurePlotly(sanfig)

            with solara.lab.Tab("Layers -> Web Maps", icon_name="mdi-chart-line"):
                with solara.Card():

                    solara.FigurePlotly(sanfig_solo)

            with solara.lab.Tab("Spring Layout", icon_name="mdi-chart-line"):
                with solara.Card():
                    solara.SliderInt("Node Size", value=int_value, min=30, max=70, on_value=datavalues)
                    solara.Button("Reset", on_click=lambda: int_value.set(42))
                    solara.Markdown(f"value: {int_value.value}")
                    datavalues(int_value.value)

            with solara.lab.Tab("DataFrame", icon_name="mdi-database"):
                solara.provide_cross_filter()
                with solara.Card():
                    solara.CrossFilterReport(dfsubset, classes=["py-2"])
                    solara.CrossFilterSelect(dfsubset, "map_title")
                    solara.CrossFilterDataFrame(dfsubset)

        with solara.Sidebar():
            solara.Markdown("Access Web Map Overview in Portal")
            df = dfsubset[~dfsubset['map_title'].duplicated()]
            with solara.Column(gap="12px"):
                for item in df.itertuples():
                    solara.Button(
                        f"{item.map_title}", href=f"https://geo.co.crook.or.us/portal/home/item.html?id={item.item_id}",
                        color="#AFC4D9"
                    )

    return main


