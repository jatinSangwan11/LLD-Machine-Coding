from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep

from lru_cache import LRUCache


def test_get_changes_eviction_order():
    cache = LRUCache(2)
    assert cache.get(1) == -1  # Empty-cache miss.

    cache.put(1, 100)
    cache.put(2, 200)

    assert cache.get(1) == 100

    cache.put(3, 300)

    assert cache.get(2) == -1
    assert cache.get(1) == 100
    assert cache.get(3) == 300

def test_update_preserves_entries_and_changes_eviction_order():
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)

    cache.put(1, 150)
    assert cache.get(2) == 200  # Updating a full cache must not evict key 2.

    cache.put(1, 175)
    # Insert immediately: no get should change recency before eviction.
    cache.put(3, 300)

    assert cache.get(2) == -1
    assert cache.get(1) == 175
    assert cache.get(3) == 300


def test_capacity_one_replaces_only_entry():
    cache = LRUCache(1)
    cache.put(1, 100)
    cache.put(2, 200)

    assert cache.get(1) == -1
    assert cache.get(2) == 200


# can ignore - instead we can run a demo
def test_concurrent_get_and_put_keep_cache_consistent():
    cache = LRUCache(3)     # This is the one shared cache
    worker_count = 4        # let's those threads wait until everyone is ready
    start = Barrier(worker_count)

    def worker(worker_id):
        # All workers reach this point before any starts accessing the cache.
        start.wait(timeout=5)
        for step in range(500):
            key = (step + worker_id) % 8
            cache.put(key, key * 10)
            if step % 10 == 0:
                sleep(0)  # Give other threads a chance to run between operations.
            # Another thread may have evicted this key since our put.
            assert cache.get(key) in (-1, key * 10)
            cache.get((key + 1) % 8)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(worker, i) for i in range(worker_count)]
        for future in futures:
            future.result()  # Propagate worker exceptions to pytest.

    # Workers have finished: inspect state without racing with a cache operation.
    assert 0 < len(cache.lookup) <= cache.cap
    assert cache.dll.tail.prev is None
    assert cache.dll.head.next is None

    seen = set()
    previous = None
    node = cache.dll.tail
    while node is not None:
        assert node not in seen, 'Cycle in linked list'
        seen.add(node)
        assert node.prev is previous  # Check the reverse link at each step.
        assert cache.lookup[node.key] is node
        previous, node = node, node.next

    assert previous is cache.dll.head
    assert seen == set(cache.lookup.values())
