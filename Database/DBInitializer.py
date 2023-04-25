#初始化資料庫
from Database.DBConnection import DBConnection
necessary_table_to_create = {
    "member_info":
        """
            CREATE TABLE member_info
            (
                member_id INTEGER PRIMARY KEY,
                account VARCHAR(255),
                password VARCHAR(255),
                TWD INT 
            );
        """,

    "trade_info":
        """
            CREATE TABLE trade_info
            (
                trade_id INTEGER PRIMARY KEY,
                member_id INTEGER,
                currency VARCHAR(255),
                amount FLOAT,
                date STRING,
                price Float,
                FOREIGN KEY(member_id) REFERENCES member_info(member_id)
            );
        """
}

class DBInitializer:
    def execute(self):
        existing_tables = self.get_existing_tables()
        self.create_not_exist_table(existing_tables)

    def get_existing_tables(self):
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
            records = cursor.fetchall()

        return [single_row["tbl_name"] for single_row in records]

    def create_not_exist_table(self, existing_tables):
        for necessary_table, table_creating_command in necessary_table_to_create.items():
            if necessary_table not in existing_tables:
                self.create_table_with_specefied_command(table_creating_command)

    def create_table_with_specefied_command(self, command):
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()