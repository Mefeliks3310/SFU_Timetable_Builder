# logic/main_logic.py
import os
import re
import pandas as pd
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class MainLogic:
    def __init__(self):
        self.teachers = []
        self.teachers_schedule = dict()

    def get_teacher_statuses(self):
        statuses = dict()

        for teacher_name in self.teachers_schedule:
            if type(self.teachers_schedule[teacher_name]) is dict:
                statuses[teacher_name] = "ok"
            else:
                statuses[teacher_name] = self.teachers_schedule[teacher_name]
        return statuses

    def load_data(self, file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, header=None)
        else:
            return pd.read_excel(file_path, engine='openpyxl', header=None, names=["фио", "url"])

    def load_config_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.xlsx', '.xls', '.xlsm', '.xlsb', '.csv']:
            raise ValueError("Недопустимый формат файла")

        if ext == '.csv':
            df = pd.read_csv(file_path, header=None)
        else:
            df = pd.read_excel(file_path, engine='openpyxl', header=None, names=["фио", "url"])
        self.teachers.clear()
        self.teachers = df.to_dict("records")

    def create_combined_schedule(self):
        if not self.teachers:
            raise ValueError("Нет данных", "Сначала загрузите конфигурационный файл.")
        self.teachers_schedule.clear()
        for teacher in self.teachers:
            this_schedule = self.get_schedule(teacher["фио"], teacher["url"])
            if type(this_schedule) is dict:
                self.teachers_schedule[teacher["фио"]] = this_schedule
            else:
                self.teachers_schedule[teacher["фио"]] = this_schedule
        # Заглушка (в будущем сюда - логика объединения расписания)
        messagebox.showinfo("Готово", "Объединённое расписание успешно создано!")

    def get_schedule(self, teacher_name, url):
        f"""
            Создание словаря с расписанием для преподавателя (ФИО преподавателя, url)
            teacher_name - Иванов А. В.
            url - ссылка на расписание преподавателя
        """
        # Получаем HTML-код страницы
        response = requests.get(url, verify=False)
        html = response.text

        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', class_='table timetable')
        if table is None:
            print("Таблица не найдена!")
            return "Таблица не найдена!"

        rows = table.find_all('tr')
        if len(rows) == 0:
            return "Неправильная ссылка на расписание"

        if teacher_name[-1] != ".":
            return "Неправильное имя преподавателя"
        if teacher_name not in html:
            return "Неправильное имя преподавателя"

        print(f"Найдено строк: {len(rows)}")

        dict_of_schedule = dict()
        current_heading = None

        def extract_text_with_commas_and_breaks(td):
            result = []
            group_names = []
            group_set = set()
            current_line = []

            for elem in td.contents:
                if isinstance(elem, NavigableString):
                    text_ = elem.strip()
                    if text_ and text_ != ',':
                        current_line.append(text_)
                elif isinstance(elem, Tag):
                    if elem.name == "br":
                        if current_line:
                            line = ' '.join(current_line).strip()
                            if line:
                                result.append(line)
                            current_line = []
                    else:
                        text_ = elem.get_text(strip=True)
                        if "подгруппа" in text_:
                            # Удаляем "(1 подгруппа)" и подобное
                            base_name = re.sub(r'\s*\(.*подгруппа\)', '', text_)
                            if base_name not in group_set:
                                group_set.add(base_name)
                                group_names.append(base_name)
                        else:
                            current_line.append(text_)

            # Добавим последнюю строку, если что-то осталось
            if current_line:
                result.append(' '.join(current_line).strip())

            # Собираем текст:
            output = ''
            if group_names:
                output += ', '.join(group_names)
            if result:
                if output:
                    output += '\n'
                output += '\n'.join(result)

            # Удаление преподавателя из строки
            output = output.replace(teacher_name + "\n", "").replace("ЭИОС\n", "ЭИОС, ")

            return output.strip()

        for num_row in range(len(rows)):
            row = rows[num_row]  # сохраняем текущую строку, чтобы не писать rows[num_row] везде

            if "heading-section" in row.get("class"):
                # print(row.get_text(separator=' ', strip=True))
                current_heading = row.get_text(separator=' ', strip=True)
                dict_of_schedule[current_heading] = []
            if "table-center" in row.get("class"):
                tds = row.find_all("td")
                if len(tds) > 3:  # если расписание четное/нечетное
                    num_of_lesson = tds[0].get_text(separator=' ', strip=True)
                    time_of_lesson = tds[1].get_text(separator=' ', strip=True)
                    text_first = extract_text_with_commas_and_breaks(tds[2]) or "Нечетная: пусто"
                    text_second = extract_text_with_commas_and_breaks(tds[3]) or "Чётная: пусто"
                    lesson_info_first = [num_of_lesson, time_of_lesson, text_first]
                    lesson_info_second = [num_of_lesson, time_of_lesson, text_second]
                    dict_of_schedule[current_heading].append(lesson_info_first)
                    dict_of_schedule[current_heading].append(lesson_info_second)

                elif len(tds) == 3:
                    num_of_lesson = tds[0].get_text(separator=' ', strip=True)
                    time_of_lesson = tds[1].get_text(separator=' ', strip=True)
                    text = extract_text_with_commas_and_breaks(tds[2])
                    lesson_info = [num_of_lesson, time_of_lesson, text]
                    dict_of_schedule[current_heading].append(lesson_info)
        return dict_of_schedule

    #get_schedule("Кушнаренко А. В.", "https://edu.sfu-kras.ru/timetable?teacher=Кушнаренко+А.+В.")
