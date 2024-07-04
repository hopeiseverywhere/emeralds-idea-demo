import osmnx as ox
import networkx as nx
import geopandas as gpd
import json
from shapely.geometry import LineString

# Load the GeoJSON data for hospitals and power plants from the src folder
with open('src/hospitals.geojson', 'r') as f:
    hospitals_geojson = json.load(f)

with open('src/powerplants.geojson', 'r') as f:
    powerplants_geojson = json.load(f)

# Convert GeoJSON to GeoDataFrames
hospitals_gdf = gpd.GeoDataFrame.from_features(hospitals_geojson["features"])
powerplants_gdf = gpd.GeoDataFrame.from_features(powerplants_geojson["features"])

# Filter power plants to only include those in King County
powerplants_gdf = powerplants_gdf[powerplants_gdf['COUNTY'] == 'KING']

# Load or create the road network graph
place_name = "Seattle, Washington, USA"
G = ox.graph_from_place(place_name, network_type='drive')

# Convert latitude and longitude to the correct order for nearest_nodes function
hospitals_gdf['x'] = hospitals_gdf.geometry.x
hospitals_gdf['y'] = hospitals_gdf.geometry.y
powerplants_gdf['x'] = powerplants_gdf.geometry.x
powerplants_gdf['y'] = powerplants_gdf.geometry.y

# Verify that 'x' and 'y' columns exist
assert 'x' in hospitals_gdf.columns and 'y' in hospitals_gdf.columns, "Hospitals GeoDataFrame must contain 'x' and 'y' columns"
assert 'x' in powerplants_gdf.columns and 'y' in powerplants_gdf.columns, "Powerplants GeoDataFrame must contain 'x' and 'y' columns"

# Find the nearest nodes in the graph for hospitals and power plants
hospitals_gdf['nearest_node'] = ox.distance.nearest_nodes(G, X=hospitals_gdf['x'], Y=hospitals_gdf['y'])
powerplants_gdf['nearest_node'] = ox.distance.nearest_nodes(G, X=powerplants_gdf['x'], Y=powerplants_gdf['y'])

# Function to find the shortest path and length between two nodes
def find_shortest_path(G, orig, dest):
    try:
        shortest_path = nx.shortest_path(G, source=orig, target=dest, weight='length')
        shortest_path_length = nx.shortest_path_length(G, source=orig, target=dest, weight='length')
        return shortest_path, shortest_path_length
    except nx.NetworkXNoPath:
        return None, float('inf')

# Find the shortest path from each hospital to each power plant
shortest_paths = []
for _, hospital in hospitals_gdf.iterrows():
    for _, powerplant in powerplants_gdf.iterrows():
        path, length = find_shortest_path(G, hospital['nearest_node'], powerplant['nearest_node'])
        if path is not None and len(path) > 1:
            coords = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in path]
            if len(coords) > 1:
                shortest_path_info = {
                    'hospital': hospital['FACILITY'],
                    'powerplant': powerplant['NAME'],
                    'length': length,
                    'geometry': LineString(coords)
                }
                shortest_paths.append(shortest_path_info)
            else:
                print(f"Invalid coordinates for path from {hospital['FACILITY']} to {powerplant['NAME']}: {coords}")
        else:
            print(f"No valid path found from {hospital['FACILITY']} to {powerplant['NAME']}")

# Convert the shortest paths to a GeoDataFrame
shortest_paths_gdf = gpd.GeoDataFrame(shortest_paths, geometry='geometry', crs='EPSG:4326')

# Save the shortest paths to a GeoJSON file
shortest_paths_gdf.to_file('shortest_paths.geojson', driver='GeoJSON')
