import os
from pathlib import Path


class Node:
    def __init__(self, name, fr, code, loc, used, parent):
        self.name = name
        self.fr = fr
        self.code = code
        self.used = used
        self.parent = parent
        self.loc = loc


class HuffmanArchiver:
    def __init__(self):
        self.tree = []
        self.codes = {}

    def build_tree(self, text):
        fr = {}
        for char in text:
            fr[char] = fr.get(char, 0) + 1

        tree = []
        for elem, freq in fr.items():
            tree.append(Node(elem, freq, "", "", False, None))

        if len(tree) == 1:
            tree[0].code = "0"
            self.codes[tree[0].name] = "0"
            self.tree = tree
            return tree

        f = False
        while not f and len(tree) > 1:
            tree.sort(key=lambda x: x.fr)
            cnt = 0
            i = 0
            id_indices = []
            while cnt != 2 and i < len(tree):
                if not tree[i].used:
                    tree[i].used = True
                    id_indices.append(i)
                    cnt += 1
                i += 1

            if cnt < 2:
                break

            parent_node = Node(
                tree[id_indices[0]].name + tree[id_indices[1]].name,
                tree[id_indices[0]].fr + tree[id_indices[1]].fr,
                "", "", False, None
            )
            tree.append(parent_node)

            tree[id_indices[0]].parent = tree[-1].name
            tree[id_indices[1]].parent = tree[-1].name
            tree[id_indices[1]].loc = "1"
            tree[id_indices[0]].loc = "0"

            count = sum(1 for node in tree if not node.used)
            if count == 1:
                f = True

        for node in tree:
            if len(node.name) == 1:
                node.code = node.loc if node.loc else ""
                for other_node in tree:
                    if other_node.name != node.name and node.name in other_node.name:
                        node.code = other_node.loc + node.code if other_node.loc else node.code
                if node.code:
                    self.codes[node.name] = node.code

        self.tree = tree
        return tree

    def encode(self, text):
        if not self.codes:
            self.build_tree(text)
        return ''.join(self.codes[char] for char in text)

    def decode(self, encoded):
        if not self.codes:
            raise ValueError("Нет кодов для декодирования")

        reverse_codes = {code: char for char, code in self.codes.items()}
        decoded = ""
        current_code = ""
        for bit in encoded:
            current_code += bit
            if current_code in reverse_codes:
                decoded += reverse_codes[current_code]
                current_code = ""

        return decoded

    def collect_files(self, paths, base_path=None):
        files = []
        for path in paths:
            if os.path.isfile(path):
                if base_path:
                    rel_path = os.path.relpath(path, base_path)
                else:
                    rel_path = path
                files.append((path, rel_path))
            elif os.path.isdir(path):
                if base_path is None:
                    base_path = path
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, base_path)
                        files.append((full_path, rel_path))
        return files

    def compress(self, input_paths, output_archive=None):
        if isinstance(input_paths, str):
            input_paths = [input_paths]

        if output_archive is None:
            if len(input_paths) == 1 and os.path.isfile(input_paths[0]):
                output_archive = input_paths[0] + '.huff'
            else:
                output_archive = 'archive.huff'

        if not output_archive.endswith('.huff'):
            output_archive += '.huff'

        if len(input_paths) == 1 and os.path.isdir(input_paths[0]):
            base_path = input_paths[0]
        else:
            base_path = os.path.commonpath(input_paths) if len(input_paths) > 1 else os.path.dirname(input_paths[0])

        files = self.collect_files(input_paths, base_path)

        if not files:
            raise ValueError("Нет файлов для сжатия")

        file_contents = {}
        all_text = ""

        print(f"Чтение {len(files)} файлов...")
        for full_path, rel_path in files:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content:
                    file_contents[rel_path] = content
                    all_text += content
                    print(f"  {rel_path}: {len(content)} символов")
            except Exception as e:
                print(f"  Ошибка чтения {rel_path}: {e}")

        if not file_contents:
            raise ValueError("Нет данных для сжатия")

        original_size = sum(len(content.encode('utf-8')) for content in file_contents.values())

        print("Построение дерева Хаффмана...")
        self.build_tree(all_text)

        print("Кодирование файлов...")
        with open(output_archive, 'wb') as f:
            f.write(len(self.codes).to_bytes(2, 'big'))
            for char, code in self.codes.items():
                char_bytes = char.encode('utf-8')
                f.write(len(char_bytes).to_bytes(1, 'big'))
                f.write(char_bytes)
                code_bytes = code.encode('ascii')
                f.write(len(code_bytes).to_bytes(1, 'big'))
                f.write(code_bytes)

            f.write(len(file_contents).to_bytes(2, 'big'))

            for rel_path, content in file_contents.items():
                path_bytes = rel_path.encode('utf-8')
                f.write(len(path_bytes).to_bytes(2, 'big'))
                f.write(path_bytes)

                encoded = self.encode(content)
                encoded_bits = len(encoded)
                f.write(encoded_bits.to_bytes(4, 'big'))

                byte_array = bytearray()
                for i in range(0, len(encoded), 8):
                    byte = encoded[i:i + 8]
                    if len(byte) < 8:
                        byte = byte.ljust(8, '0')
                    byte_array.append(int(byte, 2))
                f.write(byte_array)

        compressed_size = os.path.getsize(output_archive)

        print(f"\nАрхив создан: {output_archive}")
        print(f"  Файлов: {len(file_contents)}")
        print(f"  Исходный размер: {original_size} байт")
        print(f"  Размер архива: {compressed_size} байт")
        print(f"  Коэффициент: {compressed_size / original_size * 100:.1f}%")

        return output_archive

    def decompress(self, archive_path, output_dir=None):
        if output_dir is None:
            output_dir = archive_path.replace('.huff', '_extracted')

        print(f"Чтение архива {archive_path}...")

        try:
            with open(archive_path, 'rb') as f:
                num_chars = int.from_bytes(f.read(2), 'big')
                self.codes = {}

                for _ in range(num_chars):
                    char_len = int.from_bytes(f.read(1), 'big')
                    char_bytes = f.read(char_len)
                    char = char_bytes.decode('utf-8')
                    code_len = int.from_bytes(f.read(1), 'big')
                    code_bytes = f.read(code_len)
                    code = code_bytes.decode('ascii')
                    self.codes[char] = code

                num_files = int.from_bytes(f.read(2), 'big')

                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)

                print(f"Распаковка {num_files} файлов...")

                for _ in range(num_files):
                    name_len = int.from_bytes(f.read(2), 'big')
                    name_bytes = f.read(name_len)
                    rel_path = name_bytes.decode('utf-8')

                    encoded_bits = int.from_bytes(f.read(4), 'big')
                    bytes_needed = (encoded_bits + 7) // 8
                    compressed_data = f.read(bytes_needed)

                    bit_string = ''
                    for i in range(bytes_needed):
                        if i < len(compressed_data):
                            bits = format(compressed_data[i], '08b')
                            if i == bytes_needed - 1:
                                bits = bits[:encoded_bits - i * 8]
                            bit_string += bits

                    decoded = self.decode(bit_string)

                    target_file = output_path / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, 'w', encoding='utf-8') as out:
                        out.write(decoded)

                    print(f"  {rel_path}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {archive_path} не найден")
        except Exception as e:
            raise Exception(f"Ошибка при распаковке: {e}")

        print(f"\nАрхив распакован в {output_dir}")


def main():
    archiver = HuffmanArchiver()

    while True:
        print("\n" + "=" * 50)
        print("АРХИВАТОР ХАФФМАНА")
        print("=" * 50)
        print("1. Сжать файл(ы) или папку(и)")
        print("2. Распаковать архив")
        print("3. Выход")

        choice = input("\nВыберите действие: ")

        if choice == '1':
            print("Введите пути (файлы или папки), каждый с новой строки, пустая строка - конец:")
            paths = []
            while True:
                path = input().strip()
                if not path:
                    break
                if os.path.exists(path):
                    paths.append(path)
                else:
                    print(f"Путь {path} не существует, пропускаем")

            if not paths:
                print("Не указано ни одного пути")
                continue

            output = input("Имя архива (Enter для автоматического): ")
            try:
                archiver.compress(paths, output if output else None)
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '2':
            archive_path = input("Путь к .huff архиву: ")
            if not os.path.exists(archive_path):
                print("Файл не найден")
                continue

            output = input("Директория для распаковки (Enter для автоматической): ")
            try:
                archiver.decompress(archive_path, output if output else None)
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            print("До свидания")
            break

        else:
            print("Неверный выбор")


if __name__ == "__main__":
    print("АРХИВАТОР ХАФФМАНА\n")
    main()