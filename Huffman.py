from Node import Node

class Huffman:
    def __init__(self):
        self.codes = {}
        self.tree = []

    def build_tree(self, data):
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1

        tree = []
        for byte, f in freq.items():
            tree.append(Node(byte, f, "", "", False, None))

        if len(tree) == 1:
            tree[0].code = "0"
            self.codes[tree[0].name] = "0"
            self.tree = tree
            return tree

        f = False
        counter = 0
        while not f and len(tree) > 1:
            tree.sort(key=lambda x: x.freq)
            cnt = 0
            i = 0
            indices = []
            while cnt != 2 and i < len(tree):
                if not tree[i].used:
                    tree[i].used = True
                    indices.append(i)
                    cnt += 1
                i += 1

            if cnt < 2:
                break

            counter += 1
            parent = Node(
                f"internal_{counter}",
                tree[indices[0]].freq + tree[indices[1]].freq,
                "", "", False, None
            )
            tree.append(parent)

            tree[indices[0]].parent = tree[-1].name
            tree[indices[1]].parent = tree[-1].name
            tree[indices[1]].loc = "1"
            tree[indices[0]].loc = "0"

            count = sum(1 for node in tree if not node.used)
            if count == 1:
                f = True

        for node in tree:
            if node.name is not None and isinstance(node.name, int):
                node.code = node.loc if node.loc else ""
                current = node

                while current.parent:
                    for parent_node in tree:
                        if parent_node.name == current.parent:
                            node.code = current.loc + node.code if current.loc else node.code
                            current = parent_node
                            break
                if node.code:
                    self.codes[node.name] = node.code

        self.tree = tree
        return tree

    def encode(self, data):
        if not self.codes:
            self.build_tree(data)
        return ''.join(self.codes[b] for b in data)

    def decode(self, bit_string):
        if not self.codes:
            raise ValueError("Нет кодов")

        reverse = {code: char for char, code in self.codes.items()}
        result = bytearray()
        current = ""

        for bit in bit_string:
            current += bit
            if current in reverse:
                result.append(reverse[current])
                current = ""

        return bytes(result)