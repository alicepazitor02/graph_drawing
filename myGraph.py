import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt


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
                              ("Check Flow Balance", self.check_flow_balance)]:
            tk.Button(root, text=text, command=command).pack(side=tk.LEFT)

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
        outflow_start = sum(self.graph[u][v]['flow'] for u, v in self.graph.out_edges(self.first_node))
        inflow_terminal = sum(self.graph[u][v]['flow'] for u, v in self.graph.in_edges(self.terminal_node))
        if outflow_start != inflow_terminal:
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


# Create the Tkinter root window
root = tk.Tk()
# Instantiate the graph interface
graph_interface = GraphInterface(root)
# Start the Tkinter main loop
root.mainloop()