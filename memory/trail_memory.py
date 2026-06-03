class TrailMemory:
    def __init__(self):
        self.transient_memory = {}
        self.relational_memory = {}
        self.archival_memory = {}

    def store_transient(self, key, value):
        self.transient_memory[key] = value

    def store_relational(self, key, value):
        self.relational_memory[key] = value

    def store_archival(self, key, value):
        self.archival_memory[key] = value

    def get_context(self):
        return {
            "transient": self.transient_memory,
            "relational": self.relational_memory,
            "archival": self.archival_memory
        }