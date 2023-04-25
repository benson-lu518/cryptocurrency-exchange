#這份檔案是用來對資料庫執行sql指令的
from Database.DBConnection import DBConnection
import datetime

class MemberInfoTable:
    def insert_a_member(self, account,password): #新增使用者，先檢查使用者帳號是否存在過，不存在才會把新的使用者資料寫入
        command = "SELECT * FROM member_info WHERE account='{}';".format(account)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        if record_from_db == []:
            command = "INSERT INTO member_info(account,password,TWD) VALUES  ('{}','{}',0);".format(account,password)
            with DBConnection() as connection:
                cursor = connection.cursor()
                cursor.execute(command)
                connection.commit()
            return True
        else:
            return False

    def login_check(self,account,password): #檢查登入信息，會去找使用者的帳號及密碼是否與輸入的相同
        command = "SELECT * FROM member_info WHERE account='{}';".format(account)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        if record_from_db == []:
            return False
        if [row['password'] for row in record_from_db][0] == password:
            return True
        return False

    def insert_a_trade(self, account,currency, amount,price): #執行交易，會把交易紀錄存入資料庫內
        id = self.select_a_member(account)[0]
        today = datetime.datetime.today()
        command = "INSERT INTO trade_info(member_id,currency,amount,price,date) VALUES  ('{}','{}','{}','{}','{}');".format(id,currency,amount,price,today.strftime("%Y/%m/%d"))
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
        return {"account":account,"currency":currency,"amount":amount,"price":price}

    def select_a_member(self, account): #把使用者的所有資料回傳
        command = "SELECT * FROM member_info WHERE account='{}';".format(account)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        return [(row["member_id"],row["account"],row["TWD"],row["password"]) for row in record_from_db][0]

    def change_member_password(self,account, password): #更改使用者密碼
        id = self.select_a_member(account)[0]
        command = "UPDATE member_info SET password='{}' WHERE member_id='{}';".format(password, id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()


    def update_member_money(self , account, amount): #更新使用者持有的錢
        id = self.select_a_member(account)[0]
        command = "UPDATE member_info SET TWD='{}'  WHERE member_id='{}';".format(amount, id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            return True
        return False

    def get_member_trades(self , account): #取得使用者的交易紀錄
        id = self.select_a_member(account)[0]
        command = "SELECT * from trade_info WHERE member_id='{}';".format(id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        if record_from_db == []:
            return []
        return [(row["trade_id"],row["currency"],row["amount"],row["date"],row["price"]) for row in record_from_db]
    
    def delete_member(self,account): #刪除使用者，把兩個table中關於該使用者的資料都刪除
        id = self.select_a_member(account)[0]
        command = "Delete from trade_info WHERE member_id='{}';".format(id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
        command = "Delete from member_info WHERE member_id='{}';".format(id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
        return True

    def get_member_income(self,account): #取得使用者的損益
        re = []
        id = self.select_a_member(account)[0]
        command = "SELECT currency, SUM(amount * price) as pay from trade_info WHERE member_id='{}' AND amount > 0 GROUP BY(currency)  ORDER BY(currency) ;".format(id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        pay = [(row["currency"],row["pay"]) for row in record_from_db]
        command = "SELECT currency, SUM(amount) as num from trade_info WHERE member_id='{}' GROUP BY(currency) ORDER BY(currency) ;".format(id)
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        num = [(row["currency"],row["num"]) for row in record_from_db]
        for i in range(len(pay)):
            if pay[i][0] == num[i][0] and num[i][1] > 0:
                re.append((pay[i][0], pay[i][1]/num[i][1]))
        return re
    
