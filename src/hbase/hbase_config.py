import upgrade_path

class hbaseConfig(upgrade_path.Config):
    def __init__(self, num_nodes, num_seeds):
        self.num_nodes = num_nodes
        self.num_seeds = num_seeds

