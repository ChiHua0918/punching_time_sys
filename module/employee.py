import module.connectDB as db

def employees():
    command = f"SELECT * FROM employee WHERE 1=1;"
    db.cursor.execute(command)
    result = db.cursor.fetchall()
    return result
