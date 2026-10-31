from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep

import pytest

from lfu_cache import LFUCache


def assert_consistent(cache):
    """Inspect only after workers finish (or while no operations are running)."""
    assert len(cache.key_to_node) <= cache.capacity
    seen = set()
    for frequency, dll in cache.frequency_map.items():
        assert dll.tail is not None and dll.head is not None
        assert dll.tail.prev is None and dll.head.next is None
        previous, node = None, dll.tail
        while node is not None:
            assert node not in seen, 'Cycle or node shared between groups'
            seen.add(node)
            assert node.prev is previous
            assert node.freq == frequency
            assert cache.key_to_node[node.key] is node
            previous, node = node, node.next
        assert previous is dll.head
    assert seen == set(cache.key_to_node.values())
    expected_minimum = min(cache.frequency_map, default=0)
    assert cache.lowest_frequency == expected_minimum


def test_get_promotes_and_evicts_lfu():
    cache = LFUCache(2)
    assert cache.get(99) == -1
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == 10
    assert cache.lowest_frequency == 1  # Key 2 still belongs to group 1.
    cache.put(3, 30)
    assert cache.get(2) == -1
    assert cache.get(1) == 10
    assert cache.get(3) == 30
    assert_consistent(cache)


def test_frequency_tie_evicts_lru_after_promotion():
    cache = LFUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == 10
    assert cache.get(2) == 20  # Joins existing group 2, becoming MRU.
    assert cache.lowest_frequency == 2
    assert set(cache.frequency_map) == {2}
    cache.put(3, 30)
    assert cache.get(1) == -1
    assert cache.get(2) == 20
    assert cache.get(3) == 30
    assert_consistent(cache)


def test_update_preserves_node_and_size_and_promotes():
    cache = LFUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    original = cache.key_to_node[1]
    cache.put(1, 15)
    assert cache.key_to_node[1] is original
    assert original.value == 15 and original.freq == 2
    assert set(cache.key_to_node) == {1, 2}
    # No intervening get should mask a failure to promote on update.
    cache.put(3, 30)
    assert cache.get(2) == -1
    assert cache.get(1) == 15
    assert_consistent(cache)


def test_capacity_zero_and_negative():
    with pytest.raises(ValueError):
        LFUCache(-1)
    cache = LFUCache(0)
    assert cache.put(1, 10) is None
    assert cache.get(1) == -1
    assert cache.key_to_node == {} and cache.frequency_map == {}
    assert_consistent(cache)


def test_capacity_one_reinsertion_and_empty_group_cleanup():
    cache = LFUCache(1)
    cache.put(1, -1)
    assert cache.get(1) == -1  # Stored -1 is a hit, so it still promotes.
    assert cache.key_to_node[1].freq == 2
    for _ in range(10):
        cache.get(1)
    assert set(cache.frequency_map) == {12}
    cache.put(2, 20)
    assert cache.get(1) == -1
    cache.put(1, 15)  # Reinsertion starts at 1, not its previous frequency.
    assert cache.key_to_node[1].freq == 1
    assert cache.get(2) == -1
    assert_consistent(cache)


def test_concurrent_hits_preserve_exact_frequency():
    cache = LFUCache(1)
    cache.put(1, 10)
    workers, iterations = 4, 300
    start = Barrier(workers)

    def worker():
        start.wait(timeout=5)
        for step in range(iterations):
            assert cache.get(1) == 10
            if step % 10 == 0:
                sleep(0)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker) for _ in range(workers)]
        for future in futures:
            future.result()
    assert cache.key_to_node[1].freq == 1 + workers * iterations
    assert_consistent(cache)


def test_concurrent_get_put_and_eviction_preserve_invariants():
    cache = LFUCache(3)
    workers = 4
    start = Barrier(workers)

    def worker(worker_id):
        start.wait(timeout=5)
        for step in range(500):
            key = (step + worker_id) % 8
            cache.put(key, key * 10)
            if step % 10 == 0:
                sleep(0)
            # Individual operations are atomic; this put/get pair is not.
            assert cache.get(key) in (-1, key * 10)
            cache.get((key + 1) % 8)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, i) for i in range(workers)]
        for future in futures:
            future.result()  # Worker failures must fail pytest.
    assert len(cache.key_to_node) == 3
    assert_consistent(cache)
