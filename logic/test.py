config_file = {"Кушнаренко":"https://edu.sfu-kras.ru/timetable?teacher=%D0%9A%D1%83%D1%88%D0%BD%D0%B0%D1%80%D0%B5%D0%BD%D0%BA%D0%BE+%D0%90.+%D0%92.", "Латынцев":"sdfsdf"}
for teacher in config_file:
    if "https://edu.sfu-kras.ru/timetable" in str(config_file[teacher]):
        print("Строка верная!")
    else: print("Строка неверного формата")
