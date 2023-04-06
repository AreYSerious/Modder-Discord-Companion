import os
import pickle

# function to save the cache
def save_cache(cache, CACHE_FILE):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)




test = {}

save_cache(test, f'data{os.sep}database.pickle')