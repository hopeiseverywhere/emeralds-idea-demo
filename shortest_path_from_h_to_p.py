import osmnx as ox
import networkx as nx
import geopandas as gpd
import json
import matplotlib.pyplot as plt

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
    shortest_path_info = {'hospital': hospital['FACILITY'], 'path': None, 'length': float('inf'), 'powerplant': None}
    for _, powerplant in powerplants_gdf.iterrows():
        path, length = find_shortest_path(G, hospital['nearest_node'], powerplant['nearest_node'])
        if length < shortest_path_info['length']:
            shortest_path_info['path'] = path
            shortest_path_info['length'] = length
            shortest_path_info['powerplant'] = powerplant['NAME']
    shortest_paths.append(shortest_path_info)

# Print the shortest paths
for info in shortest_paths:
    if info['path'] is not None:
        print(f"Shortest path from {info['hospital']} to {info['powerplant']}:")
        print(f"Path: {info['path']}")
        print(f"Length: {info['length']} meters")
        print()
    else:
        print(f"No path from {info['hospital']} to any power plant in King County.")

# Plot the shortest path for the first hospital as an example
if shortest_paths and shortest_paths[0]['path'] is not None:
    example_path = shortest_paths[0]['path']
    fig, ax = ox.plot_graph_route(G, example_path, route_linewidth=2, node_size=0, figsize=(10, 10), show=False, close=False)
    
    # Get the coordinates for the hospital and power plant
    hospital_coords = hospitals_gdf.loc[hospitals_gdf['FACILITY'] == shortest_paths[0]['hospital'], ['x', 'y']].values[0]
    powerplant_coords = powerplants_gdf.loc[powerplants_gdf['NAME'] == shortest_paths[0]['powerplant'], ['x', 'y']].values[0]

    # Plot the hospital and power plant points
    ax.plot(hospital_coords[0], hospital_coords[1], 'ro', markersize=10, label='Hospital')
    ax.plot(powerplant_coords[0], powerplant_coords[1], 'bo', markersize=10, label='Power Plant')

    ax.set_title(f"Shortest Path from {shortest_paths[0]['hospital']} to {shortest_paths[0]['powerplant']}")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.legend()
    plt.show()
