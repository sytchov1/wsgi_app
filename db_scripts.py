import sqlite3


REGIONS = [
    (1, 'Краснодарский край'),
    (2, 'Ростовская область'),
    (3, 'Ставоропольский край'),
]
CITIES = [
    (1, 'Краснодар', 1),
    (2, 'Кропоткин', 1),
    (3, 'Славянск', 1),
    (4, 'Ростов', 2),
    (5, 'Шахты', 2),
    (6, 'Батайск', 2),
    (7, 'Ставрополь', 3),
    (8, 'Пятигорск', 3),
    (9, 'Кисловодск', 3),
]
CREATE_DB_SCRIPT = '''
    CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL  CHECK (name != ''));

    CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (name != ''),
    region_id INTEGER NOT NULL,
    FOREIGN KEY (region_id) REFERENCES regions (id) ON DELETE CASCADE ON UPDATE CASCADE );

    CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    surname TEXT NOT NULL CHECK (surname != ''),
    name TEXT NOT NULL CHECK (name != ''),
    patronymic TEXT CHECK(patronymic != ''),
    region_id INTEGER,
    city_id INTEGER,
    phone TEXT CHECK (phone != ''),
    email TEXT CHECK(email != ''),
    content TEXT NOT NULL CHECK(content != ''),
    FOREIGN KEY (region_id) REFERENCES regions (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities (id) ON DELETE CASCADE ON UPDATE CASCADE );
'''
ADD_REGIONS_SCRIPT = '''INSERT INTO regions VALUES(?, ?);'''
ADD_CITIES_SCRIPT = '''INSERT INTO cities VALUES(?, ?, ?);'''


def create_db():
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.executescript(CREATE_DB_SCRIPT)
        cursor.executemany(ADD_REGIONS_SCRIPT, REGIONS)
        cursor.executemany(ADD_CITIES_SCRIPT, CITIES)
        connection.commit()
        cursor.close()
        print("База данных создана и заполнена тестовыми данными")
    except sqlite3.Error as error:
        print('При создании базы данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()


def get_regions():
    regions = []
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM regions')
        regions = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print('При получении данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()
    return regions


def get_cities(region):
    cities = []
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute(f'''SELECT cities.id, cities.name, regions.id
            FROM cities INNER JOIN regions ON cities.region_id = regions.id
            WHERE regions.id = "{region}"''')
        cities = [(r[0], r[1]) for r in cursor.fetchall()]
        cursor.close()
    except sqlite3.Error as error:
        print('При получении данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()
    return cities


def get_comments():
    comments = []
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute('SELECT id, surname, name, patronymic, content FROM comments')
        comments = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print('При получении данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()
    return comments


def add_comment(**kwargs):
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO comments (surname, name, patronymic, region_id, city_id, phone, email, content)
            VALUES (:surname, :name, :patronymic, :region, :city, :phone, :email, :content)''', kwargs)
        connection.commit()
        cursor.close()
        print('Запись успешно добавлена в БД')
        status = 1
    except sqlite3.Error as error:
        print('При записи данных в БД произошла ошибка', error)
        status = 0
    finally:
        if connection:
            connection.close()
    return status


def delete_comment(id):
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM comments WHERE id=?', (id,))
        connection.commit()
        cursor.close()
        print('Запись успешно удалена из БД')
        status = 1
    except sqlite3.Error as error:
        print('При удалении записи из БД произошла ошибка', error)
        status = 0
    finally:
        if connection:
            connection.close()
    return status


def get_stats_cities(region):
    cities = []
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute(f'''SELECT cities.name, count(*) AS com_count FROM comments
            INNER JOIN cities ON comments.city_id=cities.id WHERE comments.region_id="{region}"
            GROUP BY comments.city_id ORDER BY com_count DESC''')
        cities = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print('При получении данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()
    return cities


def get_stats_regions():
    regions = []
    try:
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        cursor.execute('''SELECT regions.id, regions.name, count(*) AS com_count
            FROM comments INNER JOIN regions ON comments.region_id=regions.id GROUP BY comments.region_id
            HAVING com_count>5 ORDER BY com_count DESC ''')
        regions = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print('При получении данных произошла ошибка', error)
    finally:
        if connection:
            connection.close()
    return regions
