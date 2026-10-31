from threading import Lock


class Node:
    def __init__(self, key: int, value: int) -> None:
        self.key = key
        self.value = value
        self.freq = 1
        self.prev: Node | None = None
        self.next: Node | None = None


class DoublyLinkedList:
    """One frequency group: tail/LRU -> next -> head/MRU."""

    def __init__(self) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None

    def append(self, node: Node) -> None:
        """Attach a fresh or detached node at the MRU/head end."""
        node.prev = self.head
        node.next = None
        if self.head is None:
            self.tail = node
        else:
            self.head.next = node
        self.head = node

    def remove(self, node: Node) -> None:
        """Detach a node belonging to this list, preserving both endpoints."""
        # Check singleton first: it is both head and tail.
        if self.head is node and self.tail is node:
            self.head = None
            self.tail = None
        elif self.head is node:
            self.head = node.prev
            self.head.next = None
        elif self.tail is node:
            self.tail = node.next
            self.tail.prev = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

        # Promotion reuses this exact node in another frequency group.
        node.prev = None
        node.next = None


class LFUCache:
    """Thread-safe LFU cache with LRU tie-breaking for integer keys/values.

    Only get/put are synchronized; callers must not mutate internal state.
    """

    def __init__(self, capacity: int) -> None:
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        # Lookup maps keys to nodes; frequency groups own their ordering.
        self.key_to_node: dict[int, Node] = {}
        self.frequency_map: dict[int, DoublyLinkedList] = {}
        self.lowest_frequency = 0
        # One lock protects the maps, links, values, and minimum together.
        self.lock = Lock()

    def _frequency_promotion_helper(self, node: Node) -> None:
        """Move a node to its next group; caller must hold self.lock."""
        old_frequency = node.freq
        source = self.frequency_map[old_frequency]
        source.remove(node)

        if source.head is None:
            # Empty groups must be removed to keep space proportional to capacity.
            del self.frequency_map[old_frequency]
            if self.lowest_frequency == old_frequency:
                # The promoted node guarantees that f+1 will be nonempty.
                self.lowest_frequency = old_frequency + 1

        node.freq = old_frequency + 1
        destination = self.frequency_map.get(node.freq)
        if destination is None:
            destination = DoublyLinkedList()
            self.frequency_map[node.freq] = destination

        # Latest access makes this node MRU within its new frequency group.
        destination.append(node)

    def get(self, key: int) -> int:
        # Hold across the entire operation, including promotion and return.
        with self.lock:
            node = self.key_to_node.get(key)
            if node is None:
                return -1
            self._frequency_promotion_helper(node)
            return node.value

    def put(self, key: int, value: int) -> None:
        # Hold across the entire operation, including promotion and return.
        with self.lock:
            if self.capacity == 0:
                return

            node = self.key_to_node.get(key)
            if node is not None:
                node.value = value
                self._frequency_promotion_helper(node)
                # An update must not fall through into eviction or new insertion.
                return

            if len(self.key_to_node) == self.capacity:
                source = self.frequency_map[self.lowest_frequency]
                victim = source.tail  # LRU entry among the lowest-frequency entries.
                source.remove(victim)
                del self.key_to_node[victim.key]
                if source.head is None:
                    del self.frequency_map[self.lowest_frequency]

            # Always insert into group 1, independently of any evicted group.
            destination = self.frequency_map.get(1)
            if destination is None:
                destination = DoublyLinkedList()
                self.frequency_map[1] = destination

            node = Node(key, value)
            destination.append(node)
            self.key_to_node[key] = node
            self.lowest_frequency = 1
