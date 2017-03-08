import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        
    def add_chat(self, chat_id):
        with self.connection:
            self.cursor.execute('INSERT OR REPLACE INTO settings (chat_id) VALUES (?)', (chat_id,))
    
    def get_functions(self, chat_id):
        with self.connection:
            data = self.cursor.execute('SELECT name, body, min_x, max_x, color FROM functions WHERE chat_id = ?',
                                       (chat_id,)).fetchall()
            bodies, min_xs, max_xs, colors = list(), dict(), dict(), dict()
            for name, body, min_x, max_x, color in data:
                bodies.append(body)
                min_xs[name] = min_x
                max_xs[name] = max_x
                colors[name] = color
                
            return bodies, min_xs, max_xs, colors
        
    def put_function(self, chat_id, name, body):
        with self.connection:
            self.cursor.execute('INSERT OR REPLACE INTO functions (chat_id, name, body) '
                                'VALUES (?, ?, ?)', (chat_id, name, body))
            
    def set_color(self, chat_id, name, color):
        with self.connection:
            self.cursor.execute('UPDATE functions SET color = ? WHERE chat_id = ? AND name = ?', (color, chat_id, name))
            
    def set_domain(self, chat_id, name, min_x, max_x):
        with self.connection:
            self.cursor.execute('UPDATE functions SET min_x = ?, max_x = ? WHERE chat_id = ? AND name = ?',
                                (min_x, max_x, chat_id, name))
            
    def set_limits(self, chat_id, axis, limits):
        min_name = axis + 'min'
        max_name = axis + 'max'
        query = 'UPDATE settings SET {0} = {1}, {2} = {3} ' \
                'WHERE chat_id = {4}'.format(min_name, limits[0], max_name, limits[1], chat_id)
        with self.connection:
            self.cursor.execute(query)
            
    def get_settings(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT xmin, xmax, ymin, ymax, xlabel, ylabel, grid '
                                       'FROM settings WHERE chat_id = ?', (chat_id,)).fetchone()
        
    def set_label(self, chat_id, axis, label):
        label_name = axis + 'label'
        query = 'UPDATE settings SET {0} = {1} ' \
                'WHERE chat_id = {2}'.format(label_name, '"'+label+'"', chat_id)
        with self.connection:
            self.cursor.execute(query)
            
    def set_grid(self, chat_id, mode):
        if not (mode == 'on' or mode == 'off'):
            return
        with self.connection:
            self.cursor.execute('UPDATE settings SET grid = ? WHERE chat_id = ?',
                                (mode, chat_id))
        
    def clear_functions(self, chat_id):
        with self.connection:
            self.cursor.execute('DELETE FROM functions WHERE chat_id = ?', (chat_id,))
    
    def clear_settings(self, chat_id):
        with self.connection:
            self.cursor.execute('DELETE FROM settings WHERE chat_id = ?', (chat_id,))
            self.cursor.execute('INSERT INTO settings (chat_id) VALUES (?)', (chat_id,))
            
    def clear_all(self, chat_id):
        with self.connection:
            self.cursor.execute('DELETE FROM functions WHERE chat_id = ?', (chat_id,))
            self.cursor.execute('DELETE FROM settings WHERE chat_id = ?', (chat_id,))
    
    def close(self):
        self.connection.close()
