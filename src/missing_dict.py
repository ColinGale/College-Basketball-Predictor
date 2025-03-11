class MissingDict(dict):
    def __missing__(self, key):
        return key

