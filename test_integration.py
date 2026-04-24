import unittest
import tempfile
import os
import shutil
import subprocess
import sys
from pathlib import Path


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты для проверки работы всей системы"""

    @classmethod
    def setUpClass(cls):
        """Создание временной директории и определение пути к скрипту"""
        cls.test_dir = tempfile.mkdtemp()
        cls.script_path = os.path.join(os.path.dirname(__file__), 'main.py')

    @classmethod
    def tearDownClass(cls):
        """Удаление временной директории"""
        shutil.rmtree(cls.test_dir)

    def create_test_files(self):
        """Создание тестовых файлов"""
        files = []
        for i, content in enumerate([
            b'First test file content',
            b'Second test file with different content',
            b'Third file with some repetitive data ' * 10
        ]):
            filepath = os.path.join(self.test_dir, f'test{i}.txt')
            with open(filepath, 'wb') as f:
                f.write(content)
            files.append(filepath)
        return files

    def test_command_line_compress(self):
        """Тест сжатия через командную строку"""
        files = self.create_test_files()

        archive_path = os.path.join(self.test_dir, 'test.huff')
        cmd = [
            sys.executable, self.script_path,
            'compress',
            *files,
            '-o', archive_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(archive_path))

        os.remove(archive_path)

    def test_command_line_decompress(self):
        """Тест распаковки через командную строку"""
        files = self.create_test_files()
        archive_path = os.path.join(self.test_dir, 'test.huff')

        compress_cmd = [
            sys.executable, self.script_path,
            'compress',
            *files,
            '-o', archive_path
        ]
        subprocess.run(compress_cmd, check=True, encoding='utf-8', errors='replace')

        output_dir = os.path.join(self.test_dir, 'decompressed')
        decompress_cmd = [
            sys.executable, self.script_path,
            'decompress',
            archive_path,
            '-o', output_dir
        ]

        result = subprocess.run(decompress_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_dir))

        for i in range(3):
            self.assertTrue(os.path.exists(os.path.join(output_dir, f'test{i}.txt')))

        os.remove(archive_path)
        shutil.rmtree(output_dir)

    def test_default_output_names(self):
        """Тест имен файлов по умолчанию"""
        filepath = os.path.join(self.test_dir, 'single.txt')
        with open(filepath, 'wb') as f:
            f.write(b'Test content')

        compress_cmd = [
            sys.executable, self.script_path,
            'compress',
            filepath
        ]
        result = subprocess.run(compress_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                                cwd=self.test_dir)
        self.assertEqual(result.returncode, 0)

        default_archive = os.path.join(self.test_dir, 'single.txt.huff')
        self.assertTrue(os.path.exists(default_archive))

        os.remove(default_archive)


if __name__ == '__main__':
    unittest.main()