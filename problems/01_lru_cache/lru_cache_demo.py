from lru_cache import LRUCache


def main():
    cache = LRUCache(3)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.put(3, 300)

    # Reading key 1 makes it MRU; key 2 is now LRU.
    print('get(1):', cache.get(1), '(expected 100)')

    # Inserting a new key into the full cache evicts key 2.
    cache.put(4, 400)
    print('get(2):', cache.get(2), '(expected -1: evicted)')
    print('get(4):', cache.get(4), '(expected 400)')

    # Updating a key replaces its value without adding an entry.
    cache.put(1, 150)
    print('get(1):', cache.get(1), '(expected 150: updated)')


if __name__ == '__main__':
    main()
