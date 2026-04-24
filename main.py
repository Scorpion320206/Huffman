import argparse
import sys
from Archiver import Archiver
import os


def compress_command(args):
    archiver = Archiver()

    if not args.paths:
        print("Ошибка: Не указаны файлы/папки для сжатия")
        return 1

    valid_paths = []
    for path in args.paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Предупреждение: Путь не существует - {path}")

    if not valid_paths:
        print("Ошибка: Нет существующих файлов/папок для сжатия")
        return 1

    try:
        output = archiver.compress(valid_paths, args.output)
        print(f"\nУспешно сжато в: {output}")
        return 0
    except Exception as e:
        print(f"Ошибка при сжатии: {e}")
        return 1


def decompress_command(args):
    archiver = Archiver()

    if not args.archive:
        print("Ошибка: Не указан архив для распаковки")
        return 1

    if not os.path.exists(args.archive):
        print(f"Ошибка: Архив не найден - {args.archive}")
        return 1

    try:
        archiver.decompress(args.archive, args.output)
        print(f"\nУспешно распаковано в: {args.output or args.archive.replace('.huff', '')}")
        return 0
    except Exception as e:
        print(f"Ошибка при распаковке: {e}")
        return 1


def interactive_mode():
    archiver = Archiver()

    while True:
        print("\n" + "=" * 50)
        print("АРХИВАТОР ХАФФМАНА")
        print("=" * 50)
        print("1. Сжать")
        print("2. Распаковать")
        print("3. Выход")

        choice = input("\nВыбор: ")

        if choice == '1':
            paths = []
            print("Введите пути (пустая строка - конец):")
            while True:
                p = input().strip()
                if not p:
                    break
                if os.path.exists(p):
                    paths.append(p)
                else:
                    print(f"Не существует: {p}")

            if paths:
                out = input("Имя архива (Enter - авто): ")
                try:
                    archiver.compress(paths, out if out else None)
                except Exception as e:
                    print(f"Ошибка: {e}")

        elif choice == '2':
            arch = input("Путь к архиву: ")
            if not os.path.exists(arch):
                print("Файл не найден")
                continue
            out = input("Папка для распаковки (Enter - авто): ")
            try:
                archiver.decompress(arch, out if out else None)
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            print("До свидания!")
            break

        else:
            print("Неверный выбор")


def main():
    if len(sys.argv) == 1:
        interactive_mode()
        return 0

    parser = argparse.ArgumentParser(
        description='Архиватор Хаффмана - сжатие и распаковка файлов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s compress file.txt -o archive.huff
  %(prog)s compress folder1 folder2 -o backup.huff
  %(prog)s decompress archive.huff -o output_folder
  %(prog)s interactive - запуск интерактивного режима
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    compress_parser = subparsers.add_parser('compress', help='Сжать файлы/папки')
    compress_parser.add_argument(
        'paths',
        nargs='+',
        help='Пути к файлам или папкам для сжатия'
    )
    compress_parser.add_argument(
        '-o', '--output',
        help='Имя выходного архива (по умолчанию: первый файл/папка + .huff)'
    )
    compress_parser.set_defaults(func=compress_command)

    decompress_parser = subparsers.add_parser('decompress', help='Распаковать архив')
    decompress_parser.add_argument(
        'archive',
        help='Путь к архиву для распаковки'
    )
    decompress_parser.add_argument(
        '-o', '--output',
        help='Папка для распаковки (по умолчанию: имя архива без .huff)'
    )
    decompress_parser.set_defaults(func=decompress_command)

    interactive_parser = subparsers.add_parser('interactive', help='Запуск в интерактивном режиме')
    interactive_parser.set_defaults(func=lambda args: interactive_mode())

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if hasattr(args, 'func'):
        return args.func(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
