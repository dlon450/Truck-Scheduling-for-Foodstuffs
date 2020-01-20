class Route(object):
    def __init__(self):
        self.nodes = []
        self.arcs = []
    def get_total_pallets(self):
        total_pallets = 0
        for node in self.nodes:
            total_pallets += node.get_pallets()
        return total_pallets
