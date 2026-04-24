import unittest
import sys
import os


def run_tests():
    """Запуск всех тестов"""
    sys.path.insert(0, os.path.dirname(__file__))

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_modules = [
        'test_huffman',
        'test_archiver',
        'test_integration',
        'test_performance'
    ]

    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"Загружены тесты из {module_name}")
        except ImportError as e:
            print(f"Предупреждение: Не удалось загрузить {module_name}: {e}")

    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())