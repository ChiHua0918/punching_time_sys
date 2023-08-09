from flask import Flask,request,jsonify
from datetime import datetime,timedelta

import module.card as card
import module.employee as employee

app = Flask(__name__)

'''
假設每一個人都只有一段班
# 正常工作時段為 8:00 - 17:30
# 中午休息時間為 12:00 - 13:30
# 上班時間不超過下班時間
'''
# clock in
@app.route("/punchIn", methods = ["POST","PATCH"])
def punchIn():
    parm = request.get_json()
    # 日常打卡
    if request.method == "POST":
        employeeNumber = int(parm["employeeNumber"])
        nowTime = datetime.now()
        todayDate = nowTime.date()
        # 查詢當天的打卡紀錄
        record = card.readCard(employeeNumber,todayDate)
        # 上班時間超過下班時間
        if nowTime > datetime.strptime(str(todayDate)+" 17:30","%Y-%m-%d %H:%M"):
            return jsonify({"msg":"Error: It's over time"}),422
        # 重複打卡
        elif record:
            return jsonify({"msg":"Error: It's already clocked in or already clocked out."}),422
        # 上班打卡失敗
        elif card.insertCard(employeeNumber,nowTime,None) == False:
            return jsonify({"msg":"Error: Fail to clock in"}),422
    # 補打卡
    elif request.method == "PATCH":
        employeeNumber = int(parm["employeeNumber"])
        # string to datetime
        clockIn = datetime.strptime(parm["time"],"%Y-%m-%d %H:%M")
        pickDate = clockIn.date()
        # 查詢今天職員的打卡情況
        record = card.readCard(employeeNumber,pickDate)
        print(record)
        # 不允許更新條件：超過正常下班時間
        if clockIn > datetime.strptime(str(pickDate)+" 17:30","%Y-%m-%d %H:%M"):
            return jsonify({"msg":"Error: Exceed regular time."}),422
        # 這天沒有上下班紀錄 -> 新增紀錄
        elif record is None:
            card.insertCard(employeeNumber,clockIn,None)
        # 不允許更新條件：已經有上班打卡紀錄
        elif record[1]:
            return jsonify({"msg":"Error: It's already clocked in."}),422
        # 不允許更新條件：補打卡時間晚於下班打卡
        elif clockIn > record[2]:
            return jsonify({"msg":"Error: The clock-out time is earlier than the clock-in time."}),422
        # 更新失敗
        elif card.updateCard(employeeNumber,clockIn,record[2],pickDate) == False:
            return jsonify({"msg":"Error: Fail to clock in"}),422

    return jsonify({"msg":"Successful"}),200
# clock out
@app.route("/punchOut", methods = ["POST","PATCH"])
def punchOut():
    parm = request.get_json()
    # 日常打卡
    if request.method == "POST":
        employeeNumber = int(parm["employeeNumber"])
        nowTime = datetime.now()
        todayDate = nowTime.date()
        # 查詢當天上班紀錄
        record = card.readCard(employeeNumber,todayDate)
        # FIXME： Exceed regular time 不確定有沒有夜班
        if nowTime < datetime.strptime(str(todayDate)+" 08:00","%Y-%m-%d %H:%M"):
            return jsonify({"msg":"Error: Exceed regular time."}),422
        # 忘記打卡上班
        elif record is None:
            card.insertCard(employeeNumber,None,nowTime)
            return jsonify({"msg":"Insert into the clock-out time."}),200
        # 重複打卡
        elif record[2]:
            return jsonify({"msg":"Error: It's already clocked out."}),422
        # 下班時間早於上班時間
        elif record[1] > nowTime:
            return jsonify({"msg":"Error: The clock-out time is earlier than the clock-in time."}),422
        # 打卡失敗
        elif card.updateCard(employeeNumber,record[1],nowTime) == False:
            return jsonify({"msg":"Error: Fail to clock out"}),422
    # 補打卡
    elif request.method == "PATCH":
        employeeNumber = int(parm["employeeNumber"])
        clockOut = parm["time"]
        # string to datetime
        clockOut = datetime.strptime(parm["time"],"%Y-%m-%d %H:%M")
        pickDate = clockOut.date()
        record = card.readCard(employeeNumber,pickDate)
        # 不允許更新條件: 早於正常上班時間 FIXME： 不確定是不是有過夜班
        if clockOut < datetime.strptime(str(pickDate)+" 08:00","%Y-%m-%d %H:%M"):
            return jsonify({"msg":"Error: Exceed regular time."}),422
        # 這天沒有上下班紀錄 -> 新增紀錄
        elif record is None:
            card.insertCard(employeeNumber,None,clockOut)
        # 不允許更新條件：已經有下班打卡紀錄
        elif record[2]:
            return jsonify({"msg":"Error: It's already clocked out."}),422
        # 不允許更新條件：補打卡時間早於上班打卡
        elif clockOut < record[1]:
            return jsonify({"msg":"Error: The clock-out time is earlier than the clock-in time."}),422
        # 更新失敗
        elif card.updateCard(employeeNumber,record[1],clockOut,pickDate) == False:
            return jsonify({"msg":"Error: Fail to clock out"}),422

    return jsonify({"msg":"Successful"}),200

# 列出所有員工當日資訊
@app.route("/todayMenbersInfo", methods = ["GET"])
def todayMenbersInfo():
    nowTime = datetime.now()
    todayDate = nowTime.date()
    menbers = employee.employees()
    print(menbers)
    result = list()
    for person in menbers:
        employeeNumber = person[0]
        record = card.readCard(employeeNumber,todayDate)
        restStart = datetime.strptime(str(todayDate)+" 12:00","%Y-%m-%d %H:%M")
        restEnd = datetime.strptime(str(todayDate)+" 13:30","%Y-%m-%d %H:%M")
        #  沒有打卡紀錄
        if record is None:
            record = (employee,None,None)
            restTime = timedelta(seconds=0)
        # 未打卡上班 或 目前為上午時段
        elif not record[1] or nowTime < restStart:
            restTime = timedelta(seconds=0)
        # 目前為中午時段 且 中午時段前打卡上班
        elif nowTime < restEnd and record[1] < restStart:
            restTime = nowTime - restStart
        # 目前為中午時段 且 中午時段打卡上班
        elif nowTime < restEnd and record[1] < restEnd:
            restTime = nowTime - record[1]
        # 目前為下午時段 且 中午時段前打卡上班
        elif nowTime > restEnd and record[1] < restStart:
            restTime = restEnd - restStart
        # 目前為下午時段 且 中午時段打卡上班
        elif nowTime > restEnd and record[1] < restEnd:
            restTime = restEnd - record[1]
        # 目前為下午時段 且 休息時間過後打卡
        elif nowTime > restEnd and record[1] > restEnd:
            restTime = timedelta(seconds=0)
        
        # 未打卡上班
        if not record[1]:
            workTime = timedelta(seconds=0)
        # 目前上班中
        elif not record[2]:
            workTime = nowTime-record[1]
        # 下班
        else:
            workTime = record[2] - record[1]

        tmp = dict()
        tmp["employeeNumber"] = employeeNumber
        tmp["clockIn"] = record[1]
        tmp["clockOut"] = record[2]
        tmp["restTime"] = restTime.total_seconds()/(60*60)
        tmp["workTime"] = (workTime - restTime).total_seconds()/(60*60)
        result.append(tmp)
    return jsonify(result)

@app.route("/pickDateMenbersInfo", methods = ["GET"])
def pickDateMenbersInfo():
    parm = request.get_json()
    # 防止日期輸入錯誤或 SQL injection
    pickDate = datetime.strptime(parm["pickDate"],"%Y-%m-%d").date()
    menbers = employee.employees()
    result = list()
    for person in menbers:
        employeeNumber = person[0]
        record = card.readCard(employeeNumber,pickDate)
        print(str(pickDate)+" 12:00")
        restStart = datetime.strptime(str(pickDate)+" 12:00","%Y-%m-%d %H:%M")
        restEnd = datetime.strptime(str(pickDate)+" 13:30","%Y-%m-%d %H:%M")
        
        # 未打卡上班或下班
        if record is None:
            record = (employee,None,None)
            restTime = timedelta(seconds=0)
            workTime = timedelta(seconds=0)
        elif not record[1] or not record[2]:
            restTime = timedelta(seconds=0)
            workTime = timedelta(seconds=0)
        # 中午時段前打卡上班
        elif record[1] < restStart:
            restTime = restEnd - restStart
            workTime = record[2] - record[1]
        # 中午時段打卡上班
        elif record[1] < restEnd:
            restTime = restEnd - record[1]
            workTime = record[2] - record[1]
        # 中午時段後打卡上班
        elif record[1] > restEnd:
            restTime = timedelta(seconds=0)
            workTime = record[2] - record[1]

        tmp = dict()
        tmp["employeeNumber"] = employeeNumber
        tmp["clockIn"] = record[1]
        tmp["clockOut"] = record[2]
        tmp["restTime"] = restTime.total_seconds()/(60*60)
        tmp["workTime"] = (workTime - restTime).total_seconds()/(60*60)
        result.append(tmp)
    return jsonify(result)

# 查詢指定日期區間未打卡下班 （若此區間未上班則不包括在內）
@app.route("/intervalNotClock", methods = ["GET"])
def intervalNotClock():
    parm = request.get_json()
    dateStart = datetime.strptime(parm["dateStart"],"%Y-%m-%d").date()
    dateEnd = datetime.strptime(parm["dateEnd"],"%Y-%m-%d").date()
    action = parm["action"]
    data = card.interval(dateStart,dateEnd)
    result = list()
    for row in data:
        if row[action] is None:
            result.append(row["employeeNumber"])
    return jsonify(result)

@app.route("/rank", methods = ["GET"])
def rank():
    parm = request.get_json()
    pickDate = datetime.strptime(parm["pickDate"],"%Y-%m-%d").date()
    num = parm["num"]
    data = card.getRank(pickDate,num)
    result = list()
    for row in data:
        result.append(row["employeeNumber"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=8000)