class Entity:
    def __init__(self, *components):
        self.components = {type(com): com for com in components}

    def __getitem__(self, key):
        return self.components[key]

    def __contains__(self, key):
        return key in self.components
