import unittest
import tempfile
import os
import shutil
from pathlib import Path
from Archiver import Archiver


class TestArchiver(unittest.TestCase):

    def setUp(self):
        """Создание временной директории для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.archiver = Archiver()

    def tearDown(self):
        """Удаление временной директории"""
        shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content):
        """Вспомогательный метод для создания тестового файла"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath

    def test_compress_single_file(self):
        """Тест сжатия одного файла"""
        content = b'Hello World! This is a test file for compression.'
        filepath = self.create_test_file('test.txt', content)

        archive_path = self.archiver.compress([filepath])

        self.assertTrue(os.path.exists(archive_path))
        self.assertTrue(archive_path.endswith('.huff'))
        self.assertGreater(os.path.getsize(archive_path), 0)

        os.remove(archive_path)

    def test_compress_multiple_files(self):
        """Тест сжатия нескольких файлов"""
        files = []

        for i in range(3):
            content = f'Content of file {i} ' * 100
            filepath = self.create_test_file(f'test{i}.txt', content.encode())
            files.append(filepath)

        archive_path = self.archiver.compress(files)
        self.assertTrue(os.path.exists(archive_path))

        os.remove(archive_path)

    def test_compress_directory(self):
        """Тест сжатия директории"""
        subdir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(subdir)

        self.create_test_file('file1.txt', b'Content 1')
        self.create_test_file('file2.txt', b'Content 2')
        self.create_test_file(os.path.join('subdir', 'file3.txt'), b'Content 3')

        archive_path = self.archiver.compress([self.test_dir])
        self.assertTrue(os.path.exists(archive_path))

        os.remove(archive_path)

    def test_compress_decompress_single_file(self):
        """Тест сжатия и распаковки одного файла"""
        original_content = b'This is the original content for compression test.'
        filepath = self.create_test_file('original.txt', original_content)

        archive_path = self.archiver.compress([filepath])

        output_dir = os.path.join(self.test_dir, 'decompressed')
        self.archiver.decompress(archive_path, output_dir)

        decompressed_file = os.path.join(output_dir, 'original.txt')
        self.assertTrue(os.path.exists(decompressed_file))

        with open(decompressed_file, 'rb') as f:
            decompressed_content = f.read()

        self.assertEqual(original_content, decompressed_content)

        os.remove(archive_path)
        shutil.rmtree(output_dir)

    def test_compress_decompress_multiple_files(self):
        """Тест сжатия и распаковки нескольких файлов"""
        expected_contents = {}

        for i in range(3):
            content = f'Content of file number {i} ' * 50
            expected_contents[f'test{i}.txt'] = content.encode()
            self.create_test_file(f'test{i}.txt', content.encode())

        archive_path = self.archiver.compress([os.path.join(self.test_dir, f'test{i}.txt') for i in range(3)])

        output_dir = os.path.join(self.test_dir, 'decompressed')
        self.archiver.decompress(archive_path, output_dir)

        for filename, expected_content in expected_contents.items():
            decompressed_file = os.path.join(output_dir, filename)
            self.assertTrue(os.path.exists(decompressed_file))

            with open(decompressed_file, 'rb') as f:
                decompressed_content = f.read()

            self.assertEqual(expected_content, decompressed_content)

        os.remove(archive_path)
        shutil.rmtree(output_dir)

    def test_compress_decompress_directory_structure(self):
        """Тест сохранения структуры директорий"""
        os.makedirs(os.path.join(self.test_dir, 'dir1', 'dir2'))

        self.create_test_file('root.txt', b'Root file')
        self.create_test_file(os.path.join('dir1', 'file1.txt'), b'File in dir1')
        self.create_test_file(os.path.join('dir1', 'dir2', 'file2.txt'), b'File in dir2')

        archive_path = self.archiver.compress([self.test_dir])

        output_dir = os.path.join(self.test_dir, 'decompressed')
        self.archiver.decompress(archive_path, output_dir)

        self.assertTrue(os.path.exists(os.path.join(output_dir, 'root.txt')))
        self.assertTrue(os.path.exists(os.path.join(output_dir, 'dir1', 'file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(output_dir, 'dir1', 'dir2', 'file2.txt')))

        os.remove(archive_path)
        shutil.rmtree(output_dir)

    def test_binary_file(self):
        """Тест сжатия бинарного файла"""
        content = bytes([i % 256 for i in range(1000)])
        filepath = self.create_test_file('binary.bin', content)

        archive_path = self.archiver.compress([filepath])

        output_dir = os.path.join(self.test_dir, 'decompressed')
        self.archiver.decompress(archive_path, output_dir)

        decompressed_file = os.path.join(output_dir, 'binary.bin')
        with open(decompressed_file, 'rb') as f:
            self.assertEqual(content, f.read())

        os.remove(archive_path)
        shutil.rmtree(output_dir)

    def test_custom_output_name(self):
        """Тест с пользовательским именем архива"""
        content = b'Test content'
        filepath = self.create_test_file('test.txt', content)

        custom_name = os.path.join(self.test_dir, 'my_archive.huff')
        archive_path = self.archiver.compress([filepath], custom_name)

        self.assertEqual(archive_path, custom_name)
        self.assertTrue(os.path.exists(archive_path))

        os.remove(archive_path)

    def test_nonexistent_file(self):
        """Тест с несуществующим файлом"""
        with self.assertRaises(Exception):
            self.archiver.compress(['nonexistent_file.txt'])

if __name__ == '__main__':
    unittest.main()