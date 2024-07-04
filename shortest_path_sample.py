import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

# Define the place to get the graph from
place_name = "Seattle, Washington, USA"

# Create the graph from the place
G = ox.graph_from_place(place_name, network_type='drive')

# Define start and end locations as (latitude, longitude)
start_point = (47.6062, -122.3321)  # Example start point (Seattle center)
end_point = (47.6097, -122.3331)    # Example end point (near Seattle center)

# Get the nearest nodes to the start and end points
orig_node = ox.distance.nearest_nodes(G, X=start_point[1], Y=start_point[0])
dest_node = ox.distance.nearest_nodes(G, X=end_point[1], Y=end_point[0])

# Calculate the shortest path
shortest_path = nx.shortest_path(G, source=orig_node, target=dest_node, weight='length')
shortest_path_length = nx.shortest_path_length(G, source=orig_node, target=dest_node, weight='length')

print(f"Shortest path: {shortest_path}")
print(f"Shortest path length: {shortest_path_length} meters")

# Print road names along the shortest path
road_names = []
for u, v in zip(shortest_path[:-1], shortest_path[1:]):
    edge_data = G.get_edge_data(u, v)
    # Get the road name, if available
    road_name = edge_data[0].get('name', 'Unnamed Road')
    road_names.append(road_name)

print("Road names along the shortest path:")
for road_name in road_names:
    print(road_name)

# Extract the nodes and edges from the graph
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

# Plot the graph with Matplotlib for interactive zoom
fig, ax = plt.subplots(figsize=(15, 15))

# Plot the edges
edges.plot(ax=ax, linewidth=1, edgecolor='black')

# Plot the nodes
nodes.plot(ax=ax, markersize=1, color='red')

# Plot the shortest path
route_nodes = nodes.loc[shortest_path]
route_nodes.plot(ax=ax, markersize=5, color='blue', zorder=3)

# Customize the plot
ax.set_title("Shortest Path Route with Zoom")
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Enable the interactive toolbar for zoom functionality
plt.show()
