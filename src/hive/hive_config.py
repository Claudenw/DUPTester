import upgrade_path

class hiveConfig(upgrade_path.Config):
    def __init__(self, num_nodes=1):
        self.num_nodes = num_nodes

