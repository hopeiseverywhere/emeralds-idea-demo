import json
import osmnx as ox

# Define the place to get the graph from
place_name = "Seattle, Washington, USA"

# Create the graph from the place
G = ox.graph_from_place(place_name, network_type='drive')

# Convert the graph to GeoDataFrames
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

# Convert nodes and edges GeoDataFrames to GeoJSON-like dictionaries
nodes_geojson = json.loads(nodes.to_json())
edges_geojson = json.loads(edges.to_json())

# Combine nodes and edges into a single FeatureCollection
combined_features = nodes_geojson['features'] + edges_geojson['features']
combined_geojson = {
    "type": "FeatureCollection",
    "features": combined_features
}

# Save the combined FeatureCollection to a pretty-printed GeoJSON file
with open("roads.geojson", "w") as f:
    json.dump(combined_geojson, f, indent=4)
