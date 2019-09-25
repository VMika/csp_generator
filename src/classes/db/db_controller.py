""" Class implementing DbController"""
import sqlite3


class DbController():
    """
    Class designed to handle database calls
    """

    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None, )
        self.cursor = self.connection.cursor()
        # Writing statement to get max id of a table since SQLite doesn't allow
        # table name as parameter in prepared statement
        self.max_id_statement = dict()
        self.max_id_statement['allowed_domain'] = \
            'SELECT MAX(id) FROM allowed_domain'
        self.max_id_statement['flag'] = \
            'SELECT MAX(csp_id) FROM flag'
        self.max_id_statement['generator'] = \
            'SELECT MAX(id) FROM generator'
        self.max_id_statement['url_list'] = \
            'SELECT MAX(session_id) FROM url_list'
        # Dictionary to keep track of last ID
        self.last_id_dict = dict()

    def add_generator(self, gen_id, start_url, allowed_domain, status):
        sql = 'INSERT INTO generator(id, start_url, allowed_domain, status) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (gen_id, start_url, allowed_domain, status))
        self.connection.commit()
        self.last_id_dict['generator'] = self.cursor.lastrowid
        return self.cursor.lastrowid

    def modify_generator_status(self, gen_id, status):
        sql = 'UPDATE generator SET status = ? WHERE id = ?'
        self.cursor.execute(sql, (status, gen_id))

    def get_all_generator(self):
        sql = "SELECT * FROM generator"
        self.cursor.execute(sql, )
        return self.cursor.fetchall()

    def add_flags(self, flags, csp_id):
        sql = 'INSERT INTO flag(csp_id, flag_info_id, location, content) VALUES (?, ?, ?, ?)'
        if flags:
            for flag in flags:
                print(type(flag.content))
                self.cursor.execute(sql, (csp_id, flag.id, flag.location, str(flag.content)))
                print(self.cursor.lastrowid)
            self.connection.commit()
        else:
            self.cursor.execute(sql, (csp_id, 0, 0, None))

    def add_crawled_url(self, gen_id, url):
        sql = 'INSERT INTO crawled_url (generator_id, url) VALUES (?,?)'
        self.cursor.execute(sql, (gen_id, url))
        self.connection.commit()

    def add_csp(self, generator_id, flags_id, url, header):
        sql = 'INSERT INTO csp(gen_id, flags_id, url, header) VALUES (?, ?, ?, ?)'
        self.cursor.execute(sql, (generator_id, flags_id, url, header))
        self.connection.commit()

    def get_all_csp(self, gen_id):
        sql = 'SELECT * FROM csp WHERE gen_id = ?'
        self.cursor.execute(sql, (gen_id,))
        return self.cursor.fetchall()

    def get_generator_by_id(self, gen_id):
        sql = 'SELECT * FROM generator WHERE id = ?'
        self.cursor.execute(sql, (gen_id,))
        return self.cursor.fetchone()

    def get_generator_status(self, gen_id):
        sql = 'SELECT status FROM generator WHERE id = ?'
        self.cursor.execute(sql, (gen_id,))
        return self.cursor.fetchone()

    def add_generator_progress(self, gen_id, total_url_number):
        sql = 'INSERT INTO generator_progress (' \
              'generator_id,' \
              'total_url_number,' \
              'processed_url_number) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (gen_id, total_url_number, 0))

    def get_generator_progress(self, gen_id):
        sql = 'SELECT processed_url_number, total_url_number FROM generator_progress WHERE generator_id = ?'
        self.cursor.execute(sql, (gen_id,))
        return self.cursor.fetchone()

    def get_flags_from_generator(self, gen_id):
        sql = """select url, content, flag_info_id, location, reco, explanation, description
        FROM generator
        inner join csp on csp.gen_id = generator.id
        inner join flag on flag.csp_id = csp.flags_id
        inner join flag_info on flag_info.id = flag.flag_info_id
        WHERE flag_info_id > 0 AND gen_id = ?
        ORDER BY url, location"""
        self.cursor.execute(sql, (gen_id,))
        return self.cursor.fetchall()

    def increment_processed_url(self, gen_id):
        sql = 'UPDATE generator_progress SET processed_url_number = processed_url_number + 1 WHERE generator_id = ?'
        self.cursor.execute(sql, (gen_id,))
        self.connection.commit()

    def clean_generator_progress(self, gen_id):
        sql = 'DELETE FROM generator_progress WHERE generator_id = ?'
        self.cursor.execute(sql, (gen_id,))
        self.connection.commit()

    def get_table_max_id(self, table):
        """
        Retrieve the max id of the table else returns 0. Will be used to deter-
        mine at which id inserting new rows.

        :param table: name of the sql table
        :return:
        """
        sql = self.max_id_statement[table]
        self.cursor.execute(sql)
        res = self.cursor.fetchone()

        return res[0] if res[0] is not None else 0
