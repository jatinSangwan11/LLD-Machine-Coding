from threading import Lock


class Node:
    def __init__(self, value, key) -> None:
        self.key = key
        self.value = value
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head: Node | None = None # MRU
        self.tail: Node | None = None # LRU

    def append(self, node: Node):
        node.prev = self.head

        if self.head is None and self.tail is None:
            self.head = node
            self.tail = node
            return

        self.head.next = node
        self.head = node

    def remove(self, node: Node):
        # Contract: node belongs to this list.
        # next points toward head/MRU; prev points toward tail/LRU.
        if node is self.head and node is self.tail:
            # Removing the only node leaves the list empty.
            self.head = None
            self.tail = None
        elif node is self.tail:
            # Advance the LRU end and disconnect it from the old tail.
            self.tail = node.next
            self.tail.prev = None
        elif node is self.head:
            # Move the MRU end back and disconnect it from the old head.
            self.head = node.prev
            self.head.next = None
        else:
            # Bypass a middle node in both directions.
            prev_node = node.prev
            next_node = node.next
            prev_node.next = next_node
            next_node.prev = prev_node

        # Every case reaches cleanup, so the node can safely be appended again.
        node.prev = None
        node.next = None

class LRUCache:

    def __init__(self, capacity) -> None:
        self.cap = capacity
        self.lookup: dict[int, Node] = {}
        self.dll: DoublyLinkedList = DoublyLinkedList()
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            if key not in self.lookup:
                return -1

            node = self.lookup[key]

            self.dll.remove(node)
            self.dll.append(node)

            return node.value
            
    def put(self, key, value):
        # Protect the dictionary and list together for the whole operation.
        with self.lock:
            if key in self.lookup:
                # Update and detach the existing node; no extra capacity is needed.
                node = self.lookup[key]
                node.value = value
                self.dll.remove(node)
            else:
                if len(self.lookup) == self.cap:
                    # Evict tail/LRU from both the list and the dictionary.
                    lru_node = self.dll.tail
                    self.dll.remove(lru_node)
                    del self.lookup[lru_node.key]

                # A new node is detached already, so do not call remove on it.
                node = Node(value, key)
                self.lookup[key] = node

            # In either case, append makes this node the head/MRU.
            self.dll.append(node)


