import module.connectDB as db
from datetime import datetime

def insertCard(employeeNumber, clockIn, clockOut):
    # covert to type datetime
    if clockIn and clockOut:
        # clockIn = datetime.strptime(clockIn, "%Y-%m-%d %H:%M")
        # clockOut = datetime.strptime(clockOut, "%Y-%m-%d %H:%M")
        command = f"INSERT INTO card (employee_number, clock_in, clock_out) VALUES ('{employeeNumber}', '{clockIn}', '{clockOut}');"
    elif clockIn:
        # clockIn = datetime.strptime(clockIn, "%Y-%m-%d %H:%M")
        command = f"INSERT INTO card (employee_number, clock_in) VALUES ('{employeeNumber}', '{clockIn}');"
    elif clockOut:
        # clockOut = datetime.strptime(clockOut, "%Y-%m-%d %H:%M")
        command = f"INSERT INTO card (employee_number, clock_out) VALUES ('{employeeNumber}', '{clockOut}');"
    try:
        db.cursor.execute(command)
        db.connection.commit()
        return True
    except Exception as e:
        print("Error in insertCard:", e)
        return False

def readCard(employeeNumber,todayDate):
    if employeeNumber:
        command = f"SELECT * FROM card WHERE employee_number = {employeeNumber} and DATE_FORMAT(clock_in, '%Y-%m-%d') = '{todayDate}';"
    else:
        command = f"SELECT * FROM card WHERE DATE_FORMAT(clock_in, '%Y-%m-%d') = '{todayDate}';"
    db.cursor.execute(command)
    result = db.cursor.fetchall() # ((employee_number,clock_in,clock_out),()...)
    # FIXME： 可能回傳兩筆資料，一個是中午，一個是下午
    return result

def updateCard(employeeNumber,clockIn,clockOut):
    if clock_in:
        command = f"UPDATE card SET clock_in = {clockIn} WHERE employee_number = {employeeNumber};"
    elif clock_out:
        command = f"UPDATE card SET clock_out = {clock_out} WHERE employee_number = {employeeNumber};"
    try:
        db.cursor.execute(command)
        db.connection.commit()
        return True
    except Exception as e:
        print("Error in updateCard:", e)
        return False

# 指定日期區間有打卡職員
def interval(timeStart,timeEnd,column):
    command = f"SELECT * FROM card WHERE {column} between '{timeStart}' and '{timeEnd}';"
    db.cursor.execute(command)
    result = db.cursor.fetchall()
    return result

# 取前幾名早到的人
def getRank(pickDate,num):
    command = f"SELECT * FROM card WHERE DATE_FORMAT(clock_in, '%Y-%m-%d') = '{pickDate}' ORDER BY 'clock_in' limit {num};"
    db.cursor.execute(command)
    result = db.cursor.fetchall()
    return result
