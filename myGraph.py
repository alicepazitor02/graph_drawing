import tkinter as tk
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt

class GraphInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Directed Graph Interface")

        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()
        self.graph = nx.DiGraph()
        self.nodes, self.edges, self.selected_nodes, self.node_objects = {}, [], [], {}

        self.canvas.bind("<Button-1>", self.on_click)

        for text, command in [("Undo", self.undo_action), ("Clear", self.clear_canvas), ("Show Graph", self.show_graph), ("Print Adjacency Matrix", self.print_adjacency_matrix)]:
            tk.Button(root, text=text, command=command).pack(side=tk.LEFT)

    def on_click(self, event):
        x, y = event.x, event.y
        clicked_node = next((n for n, (nx, ny) in self.nodes.items() if (x - nx) ** 2 + (y - ny) ** 2 <= 100), None)
        
        if clicked_node:
            self.selected_nodes.append(clicked_node)
            self.highlight_node(clicked_node)
            if len(self.selected_nodes) == 2:
                n1, n2 = self.selected_nodes
                capacity = simpledialog.askinteger("Input", f"Enter capacity for edge {n1} -> {n2}:", parent=self.root)
                if capacity is not None:
                    self.edges.append((n1, n2, self.draw_directed_edge(*self.nodes[n1], *self.nodes[n2]), capacity))
                    self.graph.add_edge(n1, n2, capacity=capacity)
                self.selected_nodes.clear()
                self.canvas.delete("highlight")
        else:
            node_id = len(self.nodes) + 1
            self.nodes[node_id] = (x, y)
            self.node_objects[node_id] = (self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="cornflower blue"), self.canvas.create_text(x, y, text=str(node_id), fill="white"))

    def highlight_node(self, node_id):
        x, y = self.nodes[node_id]
        self.canvas.create_oval(x-15, y-15, x+15, y+15, outline="red", width=2, tags="highlight")

    def draw_directed_edge(self, x1, y1, x2, y2):
        return self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="black", width=2)

    def undo_action(self):
        if self.edges:
            n1, n2, edge, _ = self.edges.pop()
            self.graph.remove_edge(n1, n2)
            self.canvas.delete(edge)
        elif self.nodes:
            last_node = max(self.nodes)
            del self.nodes[last_node], self.node_objects[last_node]
            self.graph.remove_node(last_node)
            for obj in self.node_objects.pop(last_node, []):
                self.canvas.delete(obj)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.node_objects.clear()

    def show_graph(self):
        pos = nx.spring_layout(self.graph)
        edge_labels = {(n1, n2): d["capacity"] for n1, n2, d in self.graph.edges(data=True)}
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='cornflowerblue', font_size=12, arrows=True)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()
    
    def print_adjacency_matrix(self):
        print("Adjacency Matrix:\n", nx.adjacency_matrix(self.graph).todense())

root = tk.Tk()
graph_interface = GraphInterface(root)
root.mainloop()