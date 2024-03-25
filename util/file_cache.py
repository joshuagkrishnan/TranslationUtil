import os
import pickle

class FileCache(object):
    def __init__(self, ) -> None:
        self.cache_handle = '/tmp/translator_cache.pickle'
        self.cache_data = {}
        try:
            if os.environ.get('clear_file_cache', '1'):
                os.remove(self.cache_handle)
            with open(self.cache_handle, 'rb') as handle:
                self.cache_data = pickle.load(handle)
        except FileNotFoundError:
            pass

    def update_cache(self):
        with open(self.cache_handle, 'wb') as handle:
            pickle.dump(self.cache_data, handle,
                protocol=pickle.HIGHEST_PROTOCOL)

file_cache = FileCache()