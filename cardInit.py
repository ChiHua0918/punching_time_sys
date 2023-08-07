import json
import module.card as card
import csv

def main():
    # read init data
    with open("./data/member.json","r") as file:
        data = json.load(file)
        for i in range(len(data)):
            # error key
            if "clockIn " in data[i].keys():
                data[i]["clockIn"] = data[i]['clockIn ']
                del data[i]['clockIn ']
    
    # insert into table card
    for i in range(len(data)):
        print(data[i]['employeeNumber'],data[i]['clockIn'],data[i]['clockOut'])
        card.insertCard(data[i]['employeeNumber'],data[i]['clockIn'],data[i]['clockOut'])

if __name__ == "__main__":
    main()