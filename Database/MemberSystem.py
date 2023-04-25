#這個PYTHON檔是所有從main_server的指令，並用以呼叫資料庫的function。
from Database.DBConnection import DBConnection
from Database.DBInitializer import DBInitializer
from Database.MemberInfoTable import MemberInfoTable

def delete(parameter): #刪除使用者資料
    if MemberInfoTable().delete_member(parameter["account"]):
        return {"status":"OK"}

def login(parameter): #檢查使用者登入的資訊
    if MemberInfoTable().login_check(parameter["account"],parameter["password"]):
        return {"status":"OK"}
    else:
        return {"status":"Fail","reason":"Not Found"}

def regist(parameter): #檢查使用者註冊的資訊
    if MemberInfoTable().insert_a_member(parameter["account"],parameter["password"]):
        return {"status":"OK"}
    else:
        return {"status":"Fail","reason":"Account exists"}

def member_info(parameter): #根據帳號取得使用者的基本資料
    result = MemberInfoTable().select_a_member(parameter["account"])
    return {"status":"OK","parameters":{"member_id":result[0],"account":result[1],"TWD":result[2],"password":result[3]}}

def get_member_trades(parameter): #取得使用者的交易紀錄
    result = MemberInfoTable().get_member_trades(parameter["account"])
    if result == []:
        return {"status":"Fail","reason":"No Trade Found"}
    else:
        output = []
        for trades in result:
            output.append({"key":trades[0],"info":  {"currency":trades[1],"amount":trades[2],"date":trades[3],"price":trades[4]}})
        return {"status":"OK","parameters":output}

def insert_a_trade(parameter): #執行交易
    result = MemberInfoTable().select_a_member(parameter["account"])
    if result[2] < parameter["price"] * parameter["amount"]:
        return {"status":"Fail","reason":"not enough money"}
    else:
        result = MemberInfoTable().insert_a_trade(parameter["account"],parameter["currency"],parameter["amount"],parameter["price"])
        return {"status":"OK","parameter":result}

def update_member_money(parameter): #更新使用者持有的錢
    result = MemberInfoTable().select_a_member(parameter["account"])
    if MemberInfoTable().update_member_money( parameter["account"], result[2] -  parameter["amount"]):
        return {"status":"OK"}
    return {"status":"Fail"}

def change_member_password(parameter): #換密碼
    MemberInfoTable().change_member_password(parameter["account"],parameter["password"])
    return {"status":"OK"}

def get_member_income(parameter): #取得損益表
    result = MemberInfoTable().get_member_income(parameter["account"])
    return {"status":"OK","parameter":result}
