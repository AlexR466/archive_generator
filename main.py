import random as rdm
import pandas as pd
import zipfile
import mimesis
import logging
import time
import os


class Generator:
    """Генератор. Используется для генерации данных и их сохранения.
    Вводимые пользователем данные: количество генерируемых данных (строки),
    название и тип файла для сохранения. Доступные типы файлов, в которые
    можно сохранить сгенерированные данные, хранятся
    в переменной ALLOWED_FILE_TYPES метода __init__()."""
    def __init__(self) -> None:
        logging.info('Method __init___() of Generator initialized..')
        self.COLS_COUNT: int = 12
        self.EXCEL_ROWS_LIMIT: int = 1048576
        self.MIN_RANDOM: int = 500000
        self.MAX_RANDOM: int = 2000000
        self.ENCODING: str = 'utf_8_sig'
        self.ALLOWED_FILE_TYPES: list = ['.xlsx', '.csv']
        self.df1: dict = {}
        self.df2: dict = {}

    def get_input_data(self):
        """Собирает входные данные для передачи в методы generate()
        и save_to_file(): 1. ROWS_COUNT - количество строк для генерации.
        При неудачном вводе выбирает случайное значение между
        константами MIN_RANDOM и MAX_RANDOM; 2. FILE_NAME - название файла,
        в который сохранятся данные; 3. FILE_TYPE - тип файла
        для сохранения (.csv или .xlsx). В случае, если ввод
        неверный - переходит к сохранению в файл .xlsx."""
        logging.info('Method input_data() initialized..')
        print('Enter ROWS count! MIN = 1, MAX = 2.000.000.'
              'Leave empty for random:')
        logging.info('Asked user to input ROWS_COUNT')

        try:
            ROWS_COUNT = int(input())
            logging.info('The ROWS_COUNT input is'
                         f'OK & now contains: "{ROWS_COUNT}"')
            if ROWS_COUNT < 1 or ROWS_COUNT > 2000000:
                raise ValueError
        except ValueError:
            print('Wrong or empty ROWS value. Starting to random by default..')
            logging.info('Wrong or empty ROWS value.'
                         'Starting to random by default..')
            ROWS_COUNT = rdm.randint(self.MIN_RANDOM, self.MAX_RANDOM)
            print(f'Random ROWS_COUNT is: {ROWS_COUNT}')
            logging.info(f'Random ROWS_COUNT is: "{ROWS_COUNT}"')

        print("Enter file name. Leave empty for 'output':")
        logging.info('Asked user to input FILE_NAME')

        FILE_NAME = str(input())

        if FILE_NAME:
            logging.info(f'FILE_NAME is ok & now contains: "{FILE_NAME}"')

        if not FILE_NAME:
            FILE_NAME = 'output'
            logging.info("FILE_NAME is empty, set FILE_NAME to 'output'")

        print("Enter file type: '.xlsx' or '.csv'. Leave empty for '.xlsx':")
        logging.info('Asked user to input FILE_TYPE')

        FILE_TYPE = str(input())

        if not FILE_TYPE:
            FILE_TYPE = '.xlsx'
            logging.info(f'FILE_TYPE is empty. Setting up to: "{FILE_TYPE}"')
        elif FILE_TYPE not in self.ALLOWED_FILE_TYPES:
            logging.info(f"The value of FILE_TYPE is: '{FILE_TYPE}'."
                         "It's not in the list, set to '.xlsx'")
            print('Unknown file type! Starting to save .xlsx by default..')
            FILE_TYPE = '.xlsx'

        return ROWS_COUNT, FILE_NAME, FILE_TYPE

    def generate(self, ROWS_COUNT: int):
        """Генерирует ФИО людей. Получает на вход ROWS_COUNT (количество строк)
        из метода input_data. Количество столбцов задано константой COLS_COUNT
        и равно 12 при стандартном значении."""
        logging.info('Method input_data() initialized.'
                     f'ROWS_COUNT value is: "{ROWS_COUNT}"')
        person = mimesis.Person('ru')  # Локаль для создания ФИО. Пример: ru/en

        print(f'Started generating {self.COLS_COUNT} cols,'
              f'{ROWS_COUNT} rows =>'
              f'{ROWS_COUNT*self.COLS_COUNT} fake names..')
        logging.info(f'Started generating {self.COLS_COUNT} cols,'
                     f'{ROWS_COUNT} rows =>'
                     f' {ROWS_COUNT*self.COLS_COUNT} fake names..')
        start_time = time.perf_counter()

        if ROWS_COUNT > self.EXCEL_ROWS_LIMIT:
            for col in range(self.COLS_COUNT):
                names = [person.full_name() for row
                         in range(self.EXCEL_ROWS_LIMIT)]
                self.df1[col] = names
            for col in range(self.COLS_COUNT):
                names = [person.full_name() for row
                         in range(ROWS_COUNT-self.EXCEL_ROWS_LIMIT)]
                self.df2[col] = names
        else:
            for col in range(self.COLS_COUNT):
                names = [person.full_name() for row in range(ROWS_COUNT)]
                self.df1[col] = names

        end_time = time.perf_counter()
        print(f'Success! Generated {ROWS_COUNT*self.COLS_COUNT}',
              f'fake names in {end_time - start_time} sec')
        logging.info(f'Success! Generated {ROWS_COUNT*self.COLS_COUNT}'
                     f'fake names in {end_time - start_time} sec')

    def save_to_file(self, ROWS_COUNT: int, FILE_NAME: str, FILE_TYPE: str):
        """Сохраняет сгенерированные данные в файл. Принимает в качестве
        параметра строку с типом файла: .xlsx или .csv из метода input_data().
        Если формат .xlsx и превышен лимит строк в Excel (1048576),
        разбивает данные на две части и записывает
        их в разные листы одного файла."""
        logging.info('Method save_to_file() initialized..')
        print('Started saving..')
        logging.info(f'Methods args: ROWS_COUNT: "{ROWS_COUNT}",'
                     f'FILE_NAME: "{FILE_NAME}", FILE_TYPE: "{FILE_TYPE}"')
        start_time = time.perf_counter()

        if FILE_TYPE == '.xlsx':
            if ROWS_COUNT > self.EXCEL_ROWS_LIMIT:
                data_to_save1 = pd.DataFrame(self.df1)
                data_to_save2 = pd.DataFrame(self.df2)
                logging.info('DataFrames created, starting ExcelWriter..')
                writer = pd.ExcelWriter(f'{FILE_NAME}.xlsx')
                data_to_save1.to_excel(writer, sheet_name='SheetA',
                                       index=False, header=False)
                data_to_save2.to_excel(writer, sheet_name='SheetB',
                                       index=False, header=False)
                writer.close()
                logging.info('File saved!')
            else:
                data = pd.DataFrame(self.df1)
                logging.info('DataFrame created, starting ExcelWriter..')
                data.to_excel(f'{FILE_NAME}.xlsx', index=False, header=False)
                logging.info('File saved!')
        elif FILE_TYPE == '.csv':
            data = pd.DataFrame(self.df1)
            logging.info('DataFrame created, starting to_csv() method..')
            data.to_csv(f'{FILE_NAME}.csv', index=False, header=False,
                        encoding=self.ENCODING)
            logging.info('File saved!')

        end_time = time.perf_counter()
        print(f'Success! Saved in {end_time - start_time} sec')
        logging.info(f'Saving time is: {end_time - start_time} sec')

    def ask_to_zip(self, FILE_NAME: str, FILE_TYPE: str):
        """Метод предлагает заархивировать полученные данные."""
        logging.info('Method ask_to_zip() initialized. Values: FILE_NAME:'
                     f'"{FILE_NAME}", FILE_TYPE: "{FILE_TYPE}"')
        print(f"Would you like to archive {FILE_NAME}{FILE_TYPE} to .zip?"
              "Type 'Y' or 'N':")
        logging.info('Asked user if he wants to archive'
                     f'existing "{FILE_NAME}{FILE_TYPE}" file..')

        answer = str(input())
        logging.info(f'Got users answer, it is: "{answer}"')

        FILES_TO_ARCHIVE = []
        FILES_TO_ARCHIVE.append(FILE_NAME+FILE_TYPE)

        if answer.upper() == 'Y':
            ARCH.make_archive(FILES_TO_ARCHIVE, ARCH.ask_about_archive_type())
        elif answer.upper() == 'N':
            pass
        else:
            logging.exception(f'Unknown input "{answer}", raising ValueError.')
            raise ValueError(f'Unknown input: "{answer}".'
                             'Please re-run app to archive data.')


class Archiver:
    """Упаковщик. Создает архив из входящих данных в формат zip и 7z.
    Пользователю доступны следующие варианты: архивировать готовые файлы, или
    создать новый файл, после чего сохранить его и создать архив; выбрать
    формат архива (.zip или .7z); задать максимальный размер архива."""
    def __init__(self) -> None:
        logging.info('Method __init__() of Archiver initialized..')
        self.MAXIMUM_FILE_SIZE = 4194304  # Максимальный дефолтный размер - 4GB
        self.ALLOWED_ARCHIVE_TYPES: list = ['.zip', '.7z']

    def ask_about_archiving_existing_files(self):
        """Метод дает выбор пользователю: архивировать существующие файлы
        или создать новый (Y/N). В случае неверного ввода поднимает ошибку."""
        logging.info('Method ask_about_archiving_existing_files() initialized')
        print('Would you like to archive an existing file, or create a new one?')
        print("Type 'Y' for existing file(s), or 'N' for creating a new one:")
        logging.info('Asked user to choose between existing file, '
                     'or creating a new one (Y/N)')

        answer = str(input())
        logging.info(f'Answer now contains: "{answer}"')

        if answer.upper() == 'Y':
            return True
        elif answer.upper() == 'N':
            return False
        else:
            logging.exception(f'Unknown input "{answer}", raising ValueError.')
            raise ValueError(f'Unknown input: "{answer}"')

    def choose_files_to_archive(self):
        """Метод для выбора архивируемых файлов.
        Принимает на вход количество сохраняемых файлов и их имена,
        а затем сохраняет список этих файлов в FILES_TO_ARCHIVE."""
        logging.info('Method choose_files_to_archive() initialized..')
        FILES_TO_ARCHIVE = []
        print("Input count of files that you want to archive:")
        logging.info('Asked user to input count of files that should be archived..')
        try:
            files_count = int(input())
            logging.info(f'The files_count input is OK & now contains: "{files_count}"')
            if files_count < 1:
                raise ValueError
            else:
                print("Input name of the files, that should be archived, "
                      "i.e: 'output.xlsx':")
                logging.info('Asked user to input name of the files that '
                             'should be archived..')
                FILES_TO_ARCHIVE = [input() for file_name in range(files_count)]
                logging.info(f'Got following files name: {FILES_TO_ARCHIVE}')
        except ValueError:
            logging.info(f'Arg files_count is not okay: "{files_count}". '
                         'Raising ValueError..')
            raise ValueError(f'Unknown files_count input: "{files_count}"')
        return FILES_TO_ARCHIVE

    def make_new_file_to_archive(self):
        """Метод создает новый файл, в который вносится информация
        для сохранения и архивирования. После сохранения файла, метод
        возвращает название созданного файла для дальнейшего архивирования."""
        logging.info('Method make_new_file_to_archive() initialized..')
        FILE_TO_ARCHIVE = []
        input_string = ''
        input_data = []
        print("Input strings that you want to save and archive. "
              "Type '@EOF' to stop typing:")
        logging.info('Asked user to type new file strings..')
        while input_string != '@EOF':
            input_string = input()
            input_data.append(input_string)
            logging.info(f'Added new string: "{input_string}"')
        print("Typing finished! Please type file's name, i.e. 'output.txt':")
        logging.info("Asked user to input file's name")
        file_name = input()
        logging.info(f'File name: "{file_name}". Trying to save the file..')
        with open(file_name, 'w') as file:
            for line in input_data:
                file.write(f"{line}\n")
        print(f'File "{file_name}" saved succesfully!')
        logging.info(f'File "{file_name}" saved succesfully!')
        FILE_TO_ARCHIVE.append(file_name)
        logging.info(f'File "{file_name}" added to FILE_TO_ARCHIVE. Returning..')
        return FILE_TO_ARCHIVE

    def ask_about_maximum_size(self):
        """Метод, с помощью которого пользователь задает
        максимальный размер архива (или его части). Дефолтное максимальное
        число хранится в переменной MAXIMUM_FILE_SIZE
        метода __init__() класса Archiver."""
        logging.info('Method ask_about_maximum_size() initialized..')
        print("Set the maximum archive size in KB, i.e. '1024'. "
              "Leave empty for unlimited size:")
        logging.info('Asked user to input maximum archive size')
        try:
            MAXIMUM_FILE_SIZE = int(input())
            logging.info('The MAXIMUM_FILE_SIZE input is OK & '
                         f'now contains: "{MAXIMUM_FILE_SIZE}"')
            if MAXIMUM_FILE_SIZE < 0 or not MAXIMUM_FILE_SIZE:
                raise ValueError
        except ValueError:
            print('Wrong or empty maximum archive size value. '
                  'Starting to archive with unlimited size..')
            logging.info('MAXIMUM_FILE_SIZE is wrong or empty. '
                         'Starting to archive with unlimited size..')
            MAXIMUM_FILE_SIZE = self.MAXIMUM_FILE_SIZE
            logging.info(f'MAXIMUM_FILE_SIZE is now: "{MAXIMUM_FILE_SIZE}"')
        return MAXIMUM_FILE_SIZE

    def ask_about_archive_type(self):
        """Метод, с помощью которого пользователь задает
        тип создаваемого архива (доступны .zip и .7z).
        В случае, если введенный тип пустой или
        не существует – возвращает стандартное значение .zip"""
        logging.info('Method ask_about_archive_type() initialized..')
        print("Choose archive extension: type '.zip' or '.7z'; or leave empty for '.zip':")
        logging.info('Asked user to input ARCHIVE_TYPE')

        ARCHIVE_TYPE = str(input())

        if not ARCHIVE_TYPE:
            ARCHIVE_TYPE = '.zip'
            logging.info(f'ARCHIVE_TYPE is empty. Setting up to: "{ARCHIVE_TYPE}"')
        elif ARCHIVE_TYPE not in self.ALLOWED_ARCHIVE_TYPES:
            logging.info(f"The value of ARCHIVE_TYPE is: '{ARCHIVE_TYPE}'."
                         "It's not in the list, set to '.zip'")
            print('Unknown file type! Archive extension is set to .zip by default!')
            ARCHIVE_TYPE = '.zip'

        return ARCHIVE_TYPE

    def split_archive(self, ARCHIVE_TYPE: str, MAXIMUM_FILE_SIZE: int):
        """Метод для разделения архива в случае, если превышен максимальный
        размер архива, заданный пользователем."""
        logging.info('Method split_archive() initialized..')
        file_parts_added = []
        if os.path.getsize('output' + ARCHIVE_TYPE) > MAXIMUM_FILE_SIZE*1024:
            logging.info('Archive size:'
                         f'"{os.path.getsize("output" + ARCHIVE_TYPE)}"'
                         'is more than MAXIMUM_FILE_SIZE:'
                         f'"{MAXIMUM_FILE_SIZE*1024}",'
                         'starting to split..')
            outfile = 'output' + ARCHIVE_TYPE
            packet_size = int(MAXIMUM_FILE_SIZE * 1024)
            with open(outfile, 'rb') as output:
                filecount = 0
                while True:
                    data = output.read(packet_size)
                    if not data:
                        break
                    with open("{}{:03}".format('output' + ARCHIVE_TYPE,
                                               filecount), 'wb') as packet:
                        packet.write(data)
                    file_parts_added.append("{}{:03}".format(
                        'output' + ARCHIVE_TYPE, filecount))
                    logging.info('Created file '
                                 f'{"{}{:03}".format("output" + ARCHIVE_TYPE, filecount)}')
                    filecount += 1
            packet.close()
            output.close()
            os.remove('output' + ARCHIVE_TYPE)
            with zipfile.ZipFile('final_output' + ARCHIVE_TYPE, 'w') as zip_create:
                logging.info('Starting archiving file parts..')
                for file_part in file_parts_added:
                    zip_create.write(file_part)
                    logging.info(f'Added "{file_part}" to archive!')
                    os.remove(file_part)
            zip_create.close()

    def make_archive(self, FILES_TO_ARCHIVE: list, ARCHIVE_TYPE: str,
                     MAXIMUM_FILE_SIZE: int = 4194304):
        """Метод, создающий архив из полученных файлов. Принимает на вход
        список из названий сохраняемых файлов - «FILES_TO_ARCHIVE»,
        тип архива - «ARCHIVE_TYPE» и максимальный размер архива
        (или его части) - «MAXIMUM_FILE_SIZE». """
        logging.info('Method make_archive() started'
                     f'with ARCHIVE_TYPE: "{ARCHIVE_TYPE}"..')

        with zipfile.ZipFile(f'output{ARCHIVE_TYPE}', 'w') as zip_create:
            for file in FILES_TO_ARCHIVE:
                try:
                    logging.info(f'Trying to archive file {file}'
                                 f'to {ARCHIVE_TYPE} file;'
                                 f'MAXIMUM_FILE_SIZE is "{MAXIMUM_FILE_SIZE}"')
                    zip_create.write(f'{file}',
                                     compress_type=zipfile.ZIP_DEFLATED)
                    print(f'File "{file}" added to archive..')
                    logging.info(f'File "{file}" successfully archived!')
                except FileNotFoundError:
                    logging.exception(f'File not found: "{file}",'
                                      'raising FileNotFoundError.')
                    raise FileNotFoundError(f"File {file} not found.")
        print('Files archived successfully!')
        logging.info(f'Files {FILES_TO_ARCHIVE} archived successfully!')
        zip_create.close()
        ARCH.split_archive(ARCHIVE_TYPE, MAXIMUM_FILE_SIZE)


def main() -> None:

    logging.info('Program started, method main() initialized..')

    print("Type '1' to generate data; '2' archive data:")
    logging.info('Asked user to input action type')
    action = str(input())
    logging.info(f'Variable "action" now contains: "{action}"')

    if action == '1':
        ROWS_COUNT, FILE_NAME, FILE_TYPE = GN.get_input_data()
        GN.generate(ROWS_COUNT)
        GN.save_to_file(ROWS_COUNT, FILE_NAME, FILE_TYPE)
        GN.ask_to_zip(FILE_NAME, FILE_TYPE)

    elif action == '2':
        if ARCH.ask_about_archiving_existing_files():
            FILES_TO_ARCHIVE = ARCH.choose_files_to_archive()
        else:
            FILES_TO_ARCHIVE = ARCH.make_new_file_to_archive()
        ARCHIVE_TYPE = ARCH.ask_about_archive_type()
        MAXIMUM_FILE_SIZE = ARCH.ask_about_maximum_size()
        ARCH.make_archive(FILES_TO_ARCHIVE, ARCHIVE_TYPE, MAXIMUM_FILE_SIZE)

    else:
        logging.exception(f'Unknown input "{action}", raising ValueError.')
        raise ValueError(f'Unknown input: "{action}"')


if __name__ == '__main__':
    GN = Generator()
    ARCH = Archiver()
    logging.basicConfig(filename='py_log.log', level=logging.DEBUG,
                        filemode='w', force=True,
                        format='%(asctime)s %(levelname)s %(message)s')
    main()
