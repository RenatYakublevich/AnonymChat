import sqlite3


class dbworker:
    def __init__(self,database_file):
        ''' Констуктор '''
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        '''Проверка есть ли юзер в бд'''
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `telegram_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self,telegram_username,telegram_id):
    	'''Добавляем нового юзера'''
    	with self.connection:
    		return self.cursor.execute("INSERT INTO `users` (`telegram_username`, `telegram_id`) VALUES(?,?)", (telegram_username,telegram_id))

    def edit_sex(self,sex,telegram_id):
    	'''добавление по рейтингу'''
    	with self.connection:
    		self.cursor.execute('UPDATE `users` SET `sex` = ? WHERE `telegram_id` = ?',(sex,telegram_id)) # True - мужчина, False - женщина

    def search(self,sex):
        ''' Поиск '''
        with self.connection:
            if sex == True:
                sex = False
            else:
                sex = True
            search = self.cursor.execute('SELECT `telegram_id` FROM `users` WHERE `sex` = ?',(sex)).fetchall()

            return search

    def get_info_user(self,method,telegram_id):
        ''' Получить информацию о пользователе по его айдишнику '''
        with self.connection:

            result = self.cursor.execute('SELECT `sex` FROM `users` WHERE `telegram_id` = ?',(telegram_id,)).fetchone()
            return result
