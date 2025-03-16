import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import math

class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Directed Graph Interface")

        # Create a larger canvas to draw the graph
        self.canvas = tk.Canvas(root, height=600, width=800, bg="white")
        self.canvas.pack()

        # Initialize an empty directed graph
        self.graph = nx.DiGraph()

        # Initialize structures to store graph data
        self.nodes = {}  # Stores node positions {ID -> (x, y)}
        self.edges = []  # Stores edges (from, to, drawn_edge, capacity, flow, label)
        self.selected_nodes = []  # Stores nodes selected for edge creation
        self.node_objects = {}  # Stores canvas objects (ovals and text for each node)

        # Initialize first and terminal nodes
        self.first_node = None
        self.terminal_node = None

        # Bind left click with method
        self.canvas.bind("<Button-1>", self.on_click)

        # Create buttons
        for text, command in [("Undo", self.undo_action),
                              ("Clear", self.clear_canvas),
                              ("Show Graph", self.show_graph),
                              ("Set First Node", self.set_first_node),
                              ("Set Terminal Node", self.set_terminal_node),
                              ("Check Flow Balance", self.check_flow_balance),
                              ("Residual Graph", self.residual_graph),
                              ("Generic Algorithm", self.generic_algo),
                              ("Edmonds Karp", self.edmonds_karp),
                              ("Ford Fulkerson", self.ford_fulkerson)
                              ]:
                           
            tk.Button(root, text=text, command=command).pack(side=tk.LEFT)
        self.outflow_start = 0
        self.ROW = len(self.graph)


    def get_flow(self, n1, n2, capacity):
        while True:
            flow = simpledialog.askinteger("Input", f"Enter flow for edge {n1} -> {n2} (max {capacity}): ", parent=self.root)
            if flow is None:
                flow = 0
            if capacity >= flow:
                return flow
            else:
                simpledialog.messagebox.showerror("Invalid flow", f"Flow cannot exceed capacity of {capacity}. Please enter a valid flow")

    def on_click(self, event):
        x, y = event.x, event.y

        clicked_node = next((n for n, (nx, ny) in self.nodes.items()
                             if (x - nx) ** 2 + (y - ny) ** 2 <= 100), None)

        if clicked_node:
            self.selected_nodes.append(clicked_node)
            self.highlight_node(clicked_node)

            if len(self.selected_nodes) == 2:
                n1, n2 = self.selected_nodes
                capacity = simpledialog.askinteger("Input", f"Enter capacity for edge {n1} -> {n2}: ", parent=self.root)

                if capacity is not None:
                    flow = self.get_flow(n1, n2, capacity)
                    edge = self.draw_directed_edge(*self.nodes[n1], *self.nodes[n2])

                    # Add a label to display flow and capacity on the canvas, slightly above the edge
                    mid_x = (self.nodes[n1][0] + self.nodes[n2][0]) / 2
                    mid_y = (self.nodes[n1][1] + self.nodes[n2][1]) / 2
                    offset_y = -20  # Offset the label slightly above the edge

                    label = self.canvas.create_text(mid_x, mid_y + offset_y, text=f"{flow}/{capacity}", fill="black", font=("Arial", 10))

                    # Store flow and capacity in the graph's edge attributes
                    self.graph.add_edge(n1, n2, capacity=capacity, flow=flow)

                    self.edges.append((n1, n2, edge, capacity, flow, label))

                self.selected_nodes.clear()
                self.canvas.delete("highlight")
        else:
            # If no existing node has been clicked, means we have to make a new one
            node_id = len(self.nodes) + 1
            self.nodes[node_id] = (x, y)
            self.graph.add_node(node_id)

            # Create a graphical representation of the node
            self.node_objects[node_id] = (
                self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="cornflower blue"),
                self.canvas.create_text(x, y, text=str(node_id), fill="white")
            )

    def draw_directed_edge(self, x1, y1, x2, y2):
        return self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="black", width=2)

    def highlight_node(self, node_id, highlight_color="red"):
        """Highlight a node with a specific color."""
        x, y = self.nodes[node_id]
        self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, outline=highlight_color, width=2, tags="highlight")

    def undo_action(self):
        if self.edges:
            n1, n2, edge, _, _, label = self.edges.pop()
            self.graph.remove_edge(n1, n2)
            self.canvas.delete(edge)
            self.canvas.delete(label)
        elif self.nodes:
            last_node = max(self.nodes)
            oval, text = self.node_objects[last_node]
            self.canvas.delete(oval)
            self.canvas.delete(text)
            del self.nodes[last_node], self.node_objects[last_node]
            self.graph.remove_node(last_node)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.node_objects.clear()

    def show_graph(self):
        pos = nx.spring_layout(self.graph)

        edge_labels = {}
        for n1, n2, data in self.graph.edges(data=True):
            flow = data['flow']
            capacity = data['capacity']
            edge_labels[(n1, n2)] = f"{flow}, {capacity}"

        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='cornflowerblue', font_size=12, arrows=True)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()

    def set_first_node(self):
        """Enable the user to click on a node to set it as the first (source) node."""
        messagebox.showinfo("Set First Node", "Click on a node to set it as the First Node (Source).")
        self.canvas.bind("<Button-1>", self.select_first_node)

    def set_terminal_node(self):
        """Enable the user to click on a node to set it as the terminal (sink) node."""
        messagebox.showinfo("Set Terminal Node", "Click on a node to set it as the Terminal Node (Sink).")
        self.canvas.bind("<Button-1>", self.select_terminal_node)

    def select_first_node(self, event):
        x, y = event.x, event.y

        clicked_node = next((n for n, (nx, ny) in self.nodes.items()
                             if (x - nx) ** 2 + (y - ny) ** 2 <= 100), None)

        if clicked_node:
            self.first_node = clicked_node
            self.highlight_node(clicked_node, "green")
            messagebox.showinfo("First Node Selected", f"Node {clicked_node} is selected as the First Node.")
            self.canvas.bind("<Button-1>", self.on_click)  # Reset to normal click behavior

    def select_terminal_node(self, event):
        x, y = event.x, event.y

        clicked_node = next((n for n, (nx, ny) in self.nodes.items()
                             if (x - nx) ** 2 + (y - ny) ** 2 <= 100), None)

        if clicked_node:
            self.terminal_node = clicked_node
            self.highlight_node(clicked_node, "blue")
            messagebox.showinfo("Terminal Node Selected", f"Node {clicked_node} is selected as the Terminal Node.")
            self.canvas.bind("<Button-1>", self.on_click)  # Reset to normal click behavior
    

    def check_flow_balance(self):
        # Check the flow balance for all nodes
        okay = True
        if not self.first_node or not self.terminal_node:
            messagebox.showerror("Error", "Please set both the first (source) and terminal (sink) nodes.")
            return
        self.outflow_start = sum(self.graph[u][v]['flow'] for u, v in self.graph.out_edges(self.first_node))
        inflow_terminal = sum(self.graph[u][v]['flow'] for u, v in self.graph.in_edges(self.terminal_node))
        if self.outflow_start != inflow_terminal:
            messagebox.showerror("Flow Balance Error", f"Flow into node terminal node {self.terminal_node} does not match the flow out of start node {self.first_node}.")
        else: 
            for node in self.graph.nodes:
                if node != self.first_node and node != self.terminal_node:
                    inflow = sum(self.graph[u][v]['flow'] for u, v in self.graph.in_edges(node))
                    outflow = sum(self.graph[u][v]['flow'] for u, v in self.graph.out_edges(node))
                    if(inflow != outflow) : 
                        messagebox.showerror("Flow balance error", f"Flow into node {node} does not match the flow out of the node {node}.")
                        okay = False
                        break
            if okay:
                messagebox.showinfo("OK")
                return okay   

    
    def residual_graph(self):

        if not self.check_flow_balance():
            print("Failed flow constraint")
            return
        
        residual = nx.DiGraph()
        residual.add_nodes_from(self.graph.nodes())

        for u, v, data in self.graph.edges(data=True):

            capacity = data['capacity']
            flow = data['flow']

            residual_flow = capacity - flow
            backflow = flow

            if residual.has_edge(v, u):
                residual_flow_rev = self.graph[v][u]['capacity'] - self.graph[v][u]['flow']
                backflow_rev = self.graph[v][u]['flow']
                residual_flow += backflow_rev
                backflow += residual_flow_rev
            

            #print(residual_flow, backflow)
            
            
            if residual_flow > 0:
                residual.add_edge(u, v, capacity = residual_flow)
            if backflow > 0:
                residual.add_edge(v, u, capacity = backflow)

        self.draw_residual_graph(residual)
        return residual
    
    def draw_residual_graph(self, residual):
        """Draws the residual graph with straight edges, arrows, and labels for residual capacity."""

        # Create a new Tkinter window for the residual graph
        residual_window = tk.Toplevel(self.root)
        residual_window.title("Residual Graph")

        # Create a canvas in the new window
        residual_canvas = tk.Canvas(residual_window, height=600, width=800, bg="white")
        residual_canvas.pack()

        # Draw nodes first
        for node, (x, y) in self.nodes.items():
            residual_canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="cornflower blue", outline="red")
            residual_canvas.create_text(x, y, text=str(node), fill="white", font=("Arial", 12))

        # Set to keep track of previously drawn edges (to avoid duplicate lines)
        drawn_edges = set()
        offset = 0
        off_label = 20
        # Draw edges of the residual graph with straight lines and arrows
        for u, v, data in residual.edges(data=True):
            residual_capacity = data['capacity']  # Residual capacity (not flow!)

            # Get node positions
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]

           
            if u > v:
                offset = 10
                off_label = -20    

            residual_canvas.create_line(x1, y1+offset, x2, y2 + offset, fill="purple", width=2, arrow=tk.LAST)

            # Position label for the residual capacity for u -> v
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            residual_canvas.create_text(mid_x + off_label, mid_y, text=f"{residual_capacity}", fill="red", font=("Arial", 10))

            # Mark this edge as drawn
            drawn_edges.add((u, v))
            offset = 0
            off_label = 20
        

    def dfs_find_augmenting_path(self, residual, source, sink, parent):
       
        stack = [source]

        for i in range(len(parent)):
           parent[i] = -1
        
        parent[source] = -2

        while stack:
            node = stack.pop() #LIFO - > Last in first out

            for neighbor in self.graph.neighbors(node):
                if parent[neighbor] == -1 and residual[node][neighbor]['capacity'] > 0 :
                    stack.append(neighbor)
                    parent[neighbor] = node

                    if neighbor == sink:
                        return True
        return False
       

       



    
    def bfs_find_augumenting_path(self, residual, source, sink, parent):

        """Uses BFS to find an augumenting path in the residual graph
           Updates the parent list to store the path
           Returns true if a path is found, otherwise false"""
       
        for i in range(self.graph.number_of_nodes()+ 1):
            parent[i] = -1
        queue = [source]
        parent[source] = -2  # Mark source, but it has no real parent

        while queue:
            x = queue.pop(0)  # Dequeue

            for neighbor in residual.neighbors(x):
               
                if parent[neighbor] == -1 and residual[x][neighbor]['capacity'] > 0:
                    queue.append(neighbor)
                    parent[neighbor] = x  # Store parent

                    if neighbor == sink:
                        return True  # Found augmenting path

        return False  # No path found


    def edmonds_karp(self):
        residual = self.residual_graph()
        parent = [-1] * (self.graph.number_of_nodes() + 1)  # Initialize parent list
        max_flow = 0

        source = self.first_node
        sink = self.terminal_node

        while True:
            found_path = self.bfs_find_augumenting_path(residual, source, sink, parent)
        
            if not found_path:
                break

            # Find bottleneck capacity (minimum capacity along path)
            path_flow = float('Inf')
            s = sink
            
            path = []
            path.append(sink)
            while s != source:
                path.append(s)
                path_flow = min(path_flow, residual[parent[s]][s]['capacity'])
                s = parent[s]
            path.append(source)
            path.reverse()
            print("Found Path: {", path, "}")

            # Update residual capacities
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v]['capacity'] -= path_flow

                if residual.has_edge(v, u):
                    residual[v][u]['capacity'] += path_flow
                else:
                    residual.add_edge(v, u, capacity=path_flow)  # Ensure reverse edge

                v = parent[v]

            max_flow += path_flow  # Accumulate max flow
            print("Maximum Flow", max_flow + self.outflow_start)

        return max_flow + self.outflow_start  
    
    def ford_fulkerson(self):

        residual = self.residual_graph()

        if residual is None:
            print("Residual graph not available")
        parent = [-1] * (self.graph.number_of_nodes() + 1)  # Initialize parent list
        max_flow = 0

        source = self.first_node
        sink = self.terminal_node

        while True:
            found_path = self.dfs_find_augmenting_path(residual, source, sink, parent)
        
            if not found_path:
                break

            # Find bottleneck capacity (minimum capacity along path)
            path_flow = float('Inf')
            s = sink
            
            path = []
           
            while s != source:
                path.append(s)
                path_flow = min(path_flow, residual[parent[s]][s]['capacity'])
                s = parent[s]
            path.append(source)
            path.reverse()
            print("Found Path: {", path, "}")

            # Update residual capacities
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v]['capacity'] -= path_flow

                if residual.has_edge(v, u):
                    residual[v][u]['capacity'] += path_flow
                else:
                    residual.add_edge(v, u, capacity=path_flow)  # Ensure reverse edge

                v = parent[v]

            max_flow += path_flow  # Accumulate max flow
            print("Maximum Flow", max_flow + self.outflow_start)

        return max_flow + self.outflow_start 





                

                

            

    



    
    

    
    def augument_flow_along_path(self, residual, path):
    
        aug_residual = nx.DiGraph()
        aug_residual.add_nodes_from(self.graph.nodes())

        for u, v, data in residual.edges(data=True):

            capacity = data['capacity']
            flow = data['flow']

            residual_flow = capacity - flow
            backflow = flow

            if residual.has_edge(v, u):
                residual_flow_rev = self.graph[v][u]['capacity'] - self.graph[v][u]['flow']
                backflow_rev = self.graph[v][u]['flow']
                residual_flow += backflow_rev
                backflow += residual_flow_rev

            print(residual_flow, backflow)
            
            
            if residual_flow > 0:
                residual.add_edge(u, v, capacity = residual_flow)
            if backflow > 0:
                residual.add_edge(v, u, capacity = backflow)

        self.draw_residual_graph(residual)
        return residual

    
    def generic_algo(self):
        """Computes max flow using DFS to find augmenting paths until no more exist."""

        residual = self.residual_graph()  # Get the residual graph
        if residual is None:
            print("Error: Residual graph not created.")
            return

        source = self.first_node
        sink = self.terminal_node
        max_flow = 0  # Track total flow

        while True:
            parent = {}  # Dictionary to store the path
            

            # Find an augmenting path using DFS
            found_path = self.dfs_find_augmenting_path(residual, source, sink, parent)
            if not found_path:
                break  # No more augmenting paths, terminate

            # Reconstruct the path
            path = []
            node = sink
            while node in parent:
                path.append(node)
                node = parent[node]
            path.append(source)
            path.reverse()

            print("Augmenting Path Found:", path)

            # Find the bottleneck capacity (smallest capacity along the path)
            bottleneck = float('inf')
            for i in range(len(path) - 1):
                capacity = residual[path[i]][path[i + 1]]['capacity']
                bottleneck = min(bottleneck, capacity)

            print(f"Bottleneck capacity: {bottleneck}")

            # Augment the flow along the path
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]

                # Reduce capacity in forward direction
                residual[u][v]['capacity'] -= bottleneck

                # Increase capacity in reverse direction (to allow backflow)
                if residual.has_edge(v, u):
                    residual[v][u]['capacity'] += bottleneck
                else:
                    residual.add_edge(v, u, capacity=bottleneck)

            # Update max flow
            max_flow += bottleneck
            

        print("Maximum Flow:", max_flow + self.outflow_start)
        return max_flow
    

      

    

    



                





            

# Create the Tkinter root window
root = tk.Tk()
# Instantiate the graph interface
graph_interface = GraphInterface(root)
# Start the Tkinter main loop
root.mainloop()