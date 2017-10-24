import pickle

class BasicEngine:
    def __init__(self):
        self.ranker = None
        with open('./models/ranker.pkl3', 'rb') as f:
            self.ranker = pickle.load(f)

        self.ids_map = None
        with open('./models/ids.pkl3', 'rb') as f:
            self.ids_map = pickle.load(f)

    def get_best_matches(self, query, n=10):
        ids = self.ranker.get_best_matches(query, n)
        return [self.ids_map[i] for i in ids]
