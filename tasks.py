import json
import os
import requests
import pytz

from datetime import timedelta
from datetime import datetime

from pytz import timezone
import operator
from time import mktime
import random


import requests
import hashlib
import time
import mysql.connector
import os
from dateutil.parser import parse
from pytz import timezone


def db_connection():
    # # Connect to production database
    mydb = mysql.connector.connect(
        host="tapway-dahua.cufrbzihxsda.ap-southeast-1.rds.amazonaws.com",
        user="radius",
        passwd="radtapway",
        database="dahuadb_face",
    )

    # mydb = mysql.connector.connect(
    #     host="127.0.01",
    #     user="root",
    #     port=0,
    #     passwd="tapwayabc123#",
    #     database="dahuadb_face",
    # )
    db_cursor = mydb.cursor(buffered=True, dictionary=True)
    return mydb, db_cursor


#domainip = 'http://tapwayoffice.duckdns.org/admin/API'
domainip = 'http://192.168.0.50/admin/API'
username = "system"
password = "GoTapway123#"

# Global variable: token for login authorization
TOKEN = {"token": "", "randomkey": "", "signature": ""}
connect_timeout, read_timeout = 5.0, 30.0


def pass_ecrypt(randomkey):
    # Random Key MD5 Hashing
    # randomkey = response.json()['randomKey']
    temp = hashlib.md5(password.encode())
    temp = temp.hexdigest()
    temp = hashlib.md5((username + temp).encode())
    temp = temp.hexdigest()
    temp = hashlib.md5(temp.encode())
    temp = temp.hexdigest()
    temp = hashlib.md5((username + ":DSS:" + temp).encode())
    temp = temp.hexdigest()
    signature = hashlib.md5((temp + ":" + randomkey).encode())
    signature = signature.hexdigest()
    return signature


def login():
    # First login
    # url = "{}/accounts/authorize".format(domainip)
    url = '%s/accounts/authorize' % domainip

    signature = ""
    payload = {
        "username": username,
        "input_user": "",
        "ipAddress": "",
        "clientType": "WINPC"

    }
    headers = {
        'Connection': "close",
        'Content-Type': "application/json",
        'cache-control': "no-cache",
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        # Random Key MD5 Hashing
        TOKEN['randomkey'] = response.json()['randomKey']
        print('*******')
        print(response.json())
        print(response)

        TOKEN['signature'] = pass_ecrypt(TOKEN['randomkey'])

    except Exception as e:
        print(e)

    # Second login
    payload_2 = {
        "userName": username,
        "randomKey": TOKEN['randomkey'],
        "mac": "",
        "encryptType": "MD5",
        "ipAddress": "",
        "signature": TOKEN['signature'],
        "clientType": "WINPC"
    }

    try:
        res = requests.post(url, data=json.dumps(payload_2), headers=headers)
        TOKEN["token"] = res.json().get('token')
        print('*******')
        print(res.json())
        print(res)

    except Exception as e:
        print(e)


def date_to_Asia(date):
    if type(date) is str:
        get_date_obj = parse(date)
        return get_date_obj.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))
    else:
        return date.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))


def get_age_range(age):
    if 0 <= age <= 7:
        return 1
    elif 8 <= age <= 17:
        return 2
    elif 18 <= age <= 25:
        return 3
    elif 26 <= age <= 35:
        return 4
    elif 36 <= age <= 45:
        return 5
    elif 46 <= age <= 55:
        return 6
    elif 56 <= age:
        return 7


def create_query_string(c_timestamp, y_timestamp, chids, rec_num):
    return {
        "data": {
            "page": 1,
            "pageSize": rec_num,
            "glasses": "",
            "emotion": "",
            "search": "",
            "by": "",
            "repositoryId": "",
            "channelIds": chids,
            "beginTime": y_timestamp,
            "endTime": c_timestamp,
            "beginAge": "",
            "endAge": "",
            "gender": "",
            "similarity": "",
            "imageData": "",
            "personId": "",
            "personName": "",
            "personTypeIds": [],
            "searchFromClient": "true"
        }
    }


def get_registered_camera(mydb, db_cursor):
    cameras = []
    cameras_devices = {}
    db_cursor.execute(
        "select * from face_detection_camera;"
    )
    items_found = db_cursor.fetchall()
    if len(items_found) > 0:
        for item in items_found:
            cameras.append("{}$1$0$0".format(item['device_id']))
            cameras_devices["{}$1$0$0".format(item['device_id'])] = item['id']

        return cameras, cameras_devices



def face_detection_api(c_timestamp, y_timestamp, rec_num, channelIds):
    # url = "http://192.168.0.2/admin/API/face/report/day/list"
    # url = http://192.168.0.2/admin/API/face/detection/record/feature

    url = "{}/face/detection/record/feature".format(domainip)
    payload = create_query_string(str(c_timestamp), str(y_timestamp), channelIds, rec_num)
    # querystring = {"nowTime": int(c_timestamp), "time": int(y_timestamp), "pageSize": "100000", "page": "1", "startTime": "",
    #                "endTime": "", "type": "0", "channelIds": ""}

    print(payload)

    headers = {
        'Content-Type': "application/json",
        'Connection': "keep-alive",
        'X-Subject-Token': TOKEN["token"],
        'cache-control': "no-cache",
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print('api response ..')
    print (response.json().get('data').get('pageData'))

    return response


def report_day(c_timestamp, y_timestamp, rec_num, mydb, db_cursor):

    channelIds, cameras_devices = get_registered_camera(mydb, db_cursor)

    response = face_detection_api(c_timestamp, y_timestamp, rec_num, channelIds)
    dailyresultdict = []


    if 'data' in response.json():

        data = response.json().get('data').get('pageData')

        print('item found and added to db ..{}'.format(len(data)))



        for item in data:
            db_cursor.execute(
                "select api_id from face_demographics where api_id = {} ;".format(item['id'])
            )
            item_found = db_cursor.fetchall()

            if len(item_found) == 0:
                this_id = item['id']
                this_timestamp = item['beginTime']
                this_camera_name = item['channelName']
                this_gender = item['gender']
                this_age = item['age']
                this_emotion = item['emotion']
                this_age_range = get_age_range(int(item['age']))

                # search from db the name, replace with its id
                # query_string = "SELECT * FROM face_detection_camera WHERE camera_name = '" + str(this_camera_name) + "'"
                # db_cursor.execute(query_string)
                # data = db_cursor.fetchone()
                # this_camera_id = data[0]

                # this_camera_id = item['channelId']


                this_camera_id = cameras_devices[item['channelId']]

                # insert into db
                db_cursor.execute(
                    "INSERT INTO face_demographics(api_id, timestamp, camera_id, gender, age, age_range, emotion)"
                    " VALUES ({}, {}, {}, {}, {}, {}, {});".format(this_id, this_timestamp, this_camera_id, this_gender,
                                                                   this_age, this_age_range, this_emotion)
                )

                mydb.commit()
                print('{} ********************'.format(this_id))



def reportdaily():
    mydb, db_cursor = db_connection()
    login()

    # get last hour data
    currentTime = datetime.now()
    c_timestamp = int(time.mktime(currentTime.timetuple()))
    yesterdayTime = datetime.now() - timedelta(hours=1)
    y_timestamp = int(time.mktime(yesterdayTime.timetuple()))
    records_num = 100000  # grep 100 rec from each camera every 10sec
    report_day(c_timestamp, y_timestamp, records_num, mydb, db_cursor)


def reportlive():
    mydb, db_cursor = db_connection()
    

    # get last hour data
    currentTime = datetime.now()
    c_timestamp = int(time.mktime(currentTime.timetuple()))
    # c_timestamp = int(1558573200)

    y_timestamp_start = 1561426057
    y_timestamp_end = 1561512457
    while y_timestamp_end <= c_timestamp:

        login()
        records_num = 100000  # grep 100 rec from each camera every 10sec
        print(' grab data from {} - to {} '.format(y_timestamp_start, y_timestamp_end))
        report_day(y_timestamp_end, y_timestamp_start, records_num,  mydb, db_cursor)

        y_object = datetime.fromtimestamp(y_timestamp_start)
        y_timestamp = y_object + timedelta(days=1)
        y_timestamp_start = int(time.mktime(y_timestamp.timetuple()))


        y_object_b = datetime.fromtimestamp(y_timestamp_end)
        y_timestamp_b = y_object_b + timedelta(days=1)
        y_timestamp_end = int(time.mktime(y_timestamp_b.timetuple()))
        time.sleep(30)



    # currentTime = datetime.now()
    # c_timestamp = int(time.mktime(currentTime.timetuple()))
    # # yesterdayTime = datetime.now() - timedelta(days=1)
    # # y_timestamp = int(time.mktime(yesterdayTime.timetuple()))
    #
    #
    # y_timestamp =  1558051200 #change to start date to grap data
    # y_timestamp_start = y_timestamp + 43200
    #
    # records_num = 100000  # grep 100 rec from each camera every 10sec
    #
    # while y_timestamp != c_timestamp :
    #     print(' grab data from {} - to {} '.format(y_timestamp_start, y_timestamp) )
    #     report_day(y_timestamp_start, y_timestamp, records_num)
    #     y_timestamp_start = y_timestamp + 43200
    #     y_timestamp = y_timestamp - 43200


def midnightcleansing():
    query = "DELETE n1 FROM face_demographics n1, face_demographics n2 WHERE n1.id > n2.id AND " \
            "n1.api_id = n2.api_id and n1.timestamp = n2.timestamp; "
    mydb, db_cursor = db_connection()
    db_cursor.execute(query)
    mydb.commit()


