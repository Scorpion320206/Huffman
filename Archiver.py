import os
from pathlib import Path
from Huffman import Huffman


class Archiver:
    def __init__(self):
        self.coder = Huffman()

    def _collect_files(self, paths, base_path=None):
        files = []
        for path in paths:
            if os.path.isfile(path):
                if base_path:
                    rel_path = os.path.relpath(path, base_path)
                else:
                    rel_path = os.path.basename(path)
                files.append((path, rel_path))
            elif os.path.isdir(path):
                if base_path is None:
                    base_path = path
                for root, _, filenames in os.walk(path):
                    for fname in filenames:
                        full_path = os.path.join(root, fname)
                        rel_path = os.path.relpath(full_path, base_path)
                        files.append((full_path, rel_path))
        return files

    def compress(self, paths, output_archive=None):
        if isinstance(paths, str):
            paths = [paths]

        if output_archive is None:
            if len(paths) == 1 and (os.path.isfile(paths[0]) or os.path.isdir(paths[0])):
                output_archive = paths[0] + '.huff'
            else:
                output_archive = 'archive.huff'

        if not output_archive.endswith('.huff'):
            output_archive += '.huff'

        if len(paths) == 1 and os.path.isdir(paths[0]):
            base_path = paths[0]
        else:
            try:
                base_path = os.path.commonpath(paths) if len(paths) > 1 else os.path.dirname(paths[0])
            except:
                base_path = os.path.dirname(paths[0])

        files = self._collect_files(paths, base_path)
        if not files:
            raise ValueError("Нет файлов для сжатия")

        contents = {}
        all_data = b""
        print(f"Чтение {len(files)} файлов...")

        for full_path, rel_path in files:
            try:
                with open(full_path, 'rb') as f:
                    data = f.read()
                if data:
                    contents[rel_path] = data
                    all_data += data
                    print(f"  {rel_path}: {len(data)} байт")
            except Exception as e:
                print(f"  Ошибка чтения {rel_path}: {e}")

        if not contents:
            raise ValueError("Нет данных для сжатия")

        original_size = sum(len(d) for d in contents.values())

        print("Построение дерева Хаффмана...")
        self.coder.build_tree(all_data)

        print("Кодирование файлов...")
        with open(output_archive, 'wb') as f:
            f.write(len(self.coder.codes).to_bytes(2, 'big'))
            for byte, code in self.coder.codes.items():
                f.write(bytes([byte]))
                f.write(len(code).to_bytes(2, 'big'))
                f.write(code.encode())

            f.write(len(contents).to_bytes(2, 'big'))

            for rel_path, data in contents.items():
                path_bytes = rel_path.encode('utf-8')
                f.write(len(path_bytes).to_bytes(2, 'big'))
                f.write(path_bytes)

                encoded = self.coder.encode(data)
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
        print(f"  Файлов: {len(contents)}")
        print(f"  Исходный размер: {original_size} байт")
        print(f"  Размер архива: {compressed_size} байт")
        if original_size > 0:
            print(f"  Коэффициент: {compressed_size / original_size * 100:.1f}%")

        return output_archive

    def decompress(self, archive_path, output_dir=None):
        if output_dir is None:
            output_dir = archive_path.replace('.huff', '')

        print(f"Чтение архива {archive_path}...")

        try:
            with open(archive_path, 'rb') as f:
                num_codes = int.from_bytes(f.read(2), 'big')
                codes = {}
                for _ in range(num_codes):
                    byte = f.read(1)[0]
                    code_len = int.from_bytes(f.read(2), 'big')
                    code = f.read(code_len).decode()
                    codes[byte] = code
                self.coder.codes = codes

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

                    decoded = self.coder.decode(bit_string)

                    target_file = output_path / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, 'wb') as out:
                        out.write(decoded)

                    print(f"  {rel_path}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {archive_path} не найден")
        except Exception as e:
            raise Exception(f"Ошибка при распаковке: {e}")

        print(f"\nАрхив распакован в {output_dir}")
