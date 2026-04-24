import unittest

from Huffman import Huffman


class TestHuffman(unittest.TestCase):

    def setUp(self):
        self.huffman = Huffman()

    def test_build_tree_single_byte(self):
        """Тест построения дерева для одного уникального байта"""
        data = b'aaaaaa'
        tree = self.huffman.build_tree(data)

        self.assertEqual(len(self.huffman.codes), 1)
        self.assertIn(97, self.huffman.codes)  # 97 = 'a'
        self.assertEqual(self.huffman.codes[97], "0")

    def test_build_tree_two_bytes(self):
        """Тест построения дерева для двух байтов"""
        data = b'aaaabbbb'  # 4 a и 4 b
        self.huffman.build_tree(data)

        self.assertEqual(len(self.huffman.codes), 2)
        self.assertIn(97, self.huffman.codes)
        self.assertIn(98, self.huffman.codes)

        self.assertTrue(len(self.huffman.codes[97]) > 0)
        self.assertTrue(len(self.huffman.codes[98]) > 0)

    def test_build_tree_varied_frequencies(self):
        """Тест построения дерева с разными частотами"""
        data = b'aaaabbc'  # a:4, b:2, c:1
        self.huffman.build_tree(data)

        self.assertLessEqual(len(self.huffman.codes[97]), len(self.huffman.codes[98]))
        self.assertLessEqual(len(self.huffman.codes[98]), len(self.huffman.codes[99]))

        min_length = min(len(code) for code in self.huffman.codes.values())
        self.assertEqual(len(self.huffman.codes[97]), min_length)

    def test_encode_decode(self):
        """Тест кодирования и декодирования"""
        original_data = b'hello world'
        self.huffman.build_tree(original_data)

        encoded = self.huffman.encode(original_data)
        decoded = self.huffman.decode(encoded)

        self.assertEqual(original_data, decoded)

    def test_encode_empty_data(self):
        """Тест кодирования пустых данных"""
        data = b''
        self.huffman.build_tree(data)
        encoded = self.huffman.encode(data)
        self.assertEqual(encoded, "")

    def test_decode_without_codes(self):
        """Тест декодирования без построенного дерева"""
        huffman = Huffman()
        with self.assertRaises(ValueError):
            huffman.decode("101")

    def test_large_data(self):
        """Тест на больших данных"""
        original_data = bytes([i % 256 for i in range(10000)])
        self.huffman.build_tree(original_data)

        encoded = self.huffman.encode(original_data)
        decoded = self.huffman.decode(encoded)

        self.assertEqual(original_data, decoded)

    def test_special_characters(self):
        """Тест со специальными символами"""
        original_data = b'\x00\x01\x02\x03\xff\xfe\xfd'
        self.huffman.build_tree(original_data)

        encoded = self.huffman.encode(original_data)
        decoded = self.huffman.decode(encoded)

        self.assertEqual(original_data, decoded)

    def test_repeated_single_character(self):
        """Тест с повторяющимся одним символом"""
        original_data = b'x' * 1000
        self.huffman.build_tree(original_data)

        encoded = self.huffman.encode(original_data)
        decoded = self.huffman.decode(encoded)

        self.assertEqual(original_data, decoded)
        self.assertEqual(len(self.huffman.codes[120]), 1)


class TestHuffmanCodeProperties(unittest.TestCase):
    """Тест свойств кодов Хаффмана"""

    def test_prefix_property(self):
        huffman = Huffman()
        data = b'some test data for prefix checking'
        huffman.build_tree(data)

        codes = list(huffman.codes.values())

        for i, code1 in enumerate(codes):
            for j, code2 in enumerate(codes):
                if i != j:
                    self.assertFalse(code1.startswith(code2))

    def test_optimal_encoding(self):
        """Проверка, что более частые символы имеют более короткие коды"""
        huffman = Huffman()
        data = b'a' * 1000 + b'b' * 100 + b'c' * 10 + b'd' * 1
        huffman.build_tree(data)

        self.assertTrue(len(huffman.codes[97]) <= len(huffman.codes[98]))
        self.assertTrue(len(huffman.codes[98]) <= len(huffman.codes[99]))
        self.assertTrue(len(huffman.codes[99]) <= len(huffman.codes[100]))


if __name__ == '__main__':
    unittest.main()