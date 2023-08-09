# punching_time_sys
- [API 文件](https://hackmd.io/@chi-hua/rkZ5UEqjn)
- 員工打卡資料格式
    ```json=
    {
        "employeeNumber": 1110001,
        "clockIn ": null,
        "clockOut": "2022-01-03 08:33"
    }
    ```
## 環境
- 後端： Python Flask
- Database: MySQL
- OS: Linux Ubuntu 20.04
## 目錄樹
```txt=
punching_time_sys/
├── flask/
│   ├── data
│   │   └── member.json
│   ├── module
│   │   ├── card.py
│   │   ├── connectDB.py
│   │   └── employee.py
│   ├── app.py
│   ├── init.py
│   └── db_settings.json
│   
├── README.md
└── .gitignore
```
## 使用流程
### 資料庫
- 建立資料庫 `create database clock_card;`
- 到剛剛建立的資料庫 `USE clock_card;`
- 建立資料表
    - 打卡資訊
    ```sql=
    create table card (
    employee_number int NOT NULL,
    clock_in  datetime,
    clock_out datetime
    );
    ```
    - 職員資訊
    ```sql=
    create table employee (
    employee_number int NOT NULL primary key
    );
    ```
- 新增 user `CREATE USER 'test'@'localhost' IDENTIFIED BY '@OPOPopop7788';`
- 給予權限
    ```sql=
    GRANT INSERT, SELECT, UPDATE, DELETE ON clock_card.employee TO 'test'@'localhost;
    GRANT INSERT, SELECT, UPDATE, DELETE ON clock_card.card TO 'test'@'localhost;
    ```
### 執行 Flask 前製作業
- 到 flask 資料夾 `cd flask` 
- 新增 `db_settings.json` 設定
    ```json=
    {
    "host": "localhost",
    "port": 3306,
    "user": "test",
    "password": "@OPOPopop7788",
    "database": "clock_card"
    }
    ```
- 執行 `python3 init.py` 將原本的職員資料匯入資料庫
- 執行 `python3 app.py` 執行成功畫面如下
![](https://hackmd.io/_uploads/rJdWL1b22.png)
- 即可透過 API 傳送資料
![](https://hackmd.io/_uploads/BJrAIyWnh.png)
    - 成功：200
    - 失敗：422
- 前端 receive response
![](https://hackmd.io/_uploads/rJvmOJWhn.png)
