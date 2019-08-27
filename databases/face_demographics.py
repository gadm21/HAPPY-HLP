import mysql.connector
import tasks as tasks_app

from datetime import timedelta
from datetime import datetime

import requests
import time

import json

class face_demographics():

    def __init__(self):
        #self.mydb, self.db_cursor = self.db_connection()

        self.mydb= self.db_cursor = ''
        self.data = {}
        self.age_distro = {
            "0-7": 0,
            "8-17": 0,
            "18-25": 0,
            "26-35": 0,
            "36-45": 0,
            "46-55": 0,
            "56+": 0,
        }

        self.gender_distro = {
            "female": 0,
            "male": 0
        }

        self.emotion = {
            "smile": 0,
            "anger": 0,
            "sadness": 0,
            "disgust": 0,
            "fear": 0,
            "surprised": 0,
            "normal": 0,
            "laughs": 0,
            "happy": 0,
            "confused": 0,
            "screams": 0

        }

    def get_camera_by_venue(self, venueId):
        camera_ids = []
        self.db_cursor.execute(
            "select * from face_detection_camera where venue_id = {} ;".format(venueId)
        )
        result = self.db_cursor.fetchall()
        if len(result) > 0:
            for item in result:
                camera_ids.append(item['id'])

        return camera_ids

    def db_connection(self):
        # # Connect to production database
        mydb = mysql.connector.connect(
            host="tapway-dahua.cufrbzihxsda.ap-southeast-1.rds.amazonaws.com",
            user="radius",
            passwd="radtapway",
            database="dahuadb_face",
        )

        # mydb = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     port=0,
        #     passwd="tapway",
        #     database="dahuadb_face",
        # )
        db_cursor = mydb.cursor(buffered=True, dictionary=True)
        return mydb, db_cursor

    def get_age_range(self, age):
        if 0 <= age <= 7:
            return "0-7"
        elif 8 <= age <= 17:
            return "8-17"
        elif 18 <= age <= 25:
            return "18-25"
        elif 26 <= age <= 35:
            return "26-35"
        elif 36 <= age <= 45:
            return "36-45"
        elif 46 <= age <= 55:
            return "46-55"
        elif 56 <= age:
            return "56+"

    def commulitive_data(self, item):

        age_range = self.get_age_range(int(item['age']))

        self.age_distro[str(age_range)] += 1

        if item['gender'] == '2':
            self.gender_distro['female'] += 1

        if item['gender'] == '1':
            self.gender_distro['male'] += 1

        self.emotion['smile'] = self.emotion['smile'] + 1 if item['emotion'] == "0" else self.emotion['smile']
        self.emotion['anger'] = self.emotion['anger'] + 1 if item['emotion'] == "1" else self.emotion['anger']
        self.emotion['sadness'] = self.emotion['sadness'] + 1 if item['emotion'] == "2" else self.emotion[
            'sadness']
        self.emotion['disgust'] = self.emotion['disgust'] + 1 if item['emotion'] == "3" else self.emotion[
            'disgust']
        self.emotion['fear'] = self.emotion['fear'] + 1 if item['emotion'] == "4" else self.emotion['fear']
        self.emotion['surprised'] = self.emotion['surprised'] + 1 if item['emotion'] == "5" else self.emotion[
            'surprised']
        self.emotion['normal'] = self.emotion['normal'] + 1 if item['emotion'] == "6" else self.emotion['normal']
        self.emotion['laughs'] = self.emotion['laughs'] + 1 if item['emotion'] == "7" else self.emotion['laughs']
        self.emotion['happy'] = self.emotion['happy'] + 1 if item['emotion'] == "8" else self.emotion['happy']
        self.emotion['confused'] = self.emotion['confused'] + 1 if item['emotion'] == "9" else self.emotion['confused']
        self.emotion['screams'] = self.emotion['screams'] + 1 if item['emotion'] == "10" else self.emotion['screams']



    def define_group(self, data):

        gender_f = 0
        gender_m = 0

        for gen in data :
            print('items found ....test ***')
            print(gen)
            if int(gen['gender']) == 1 :
                gender_m = gender_m + 1
            elif int(gen['gender']) == 2 :
                gender_f = gender_f + 1

        # Male

        print('F gender count ..')
        print(gender_f)
        print('M gender count ..')
        print(gender_m)

        if gender_m == len(data) :
            return "A"
        elif gender_f == len(data) :
            return "B"
        elif gender_f is not 0 and gender_m is not 0:
            return "C"



        # if len(data) == 2:
        #
        #     """ B - Male and Female (age 20 - 40)"""
        #     """ D - Male and female (age > 40) """
        #
        #     if data[0]['gender'] == '1' and data[1]['gender'] == '2':
        #         if (20 <= int(data[0]['age']) <= 40) and (20 <= int(data[1]['age']) <= 40):
        #             return 'B'
        #         elif (int(data[0]['age']) > 40) and (int(data[1]['age']) > 40):
        #             return 'D'
        #     else :
        #         return 'A' #N?A
        #
        # elif len(data) > 2:
        #     return 'E' # group more than 2 pax
        #
        #
        # elif len(data) < 2 :
        #     """ A - Male or female aged 20 - 40 """
        #     """ # C - Male or female (age > 40) """
        #
        #     for dt in data :
        #         if 20 <= int(dt['age']) <= 40:
        #             return 'A'
        #         elif int(dt['age']) > 40:
        #             return 'C'


    def get_summary_demographics_groups(self):

        tasks_app.login()

        # get last hour data
        currentTime = datetime.now()
        c_timestamp = int(time.mktime(currentTime.timetuple()))
        yesterdayTime = datetime.now() - timedelta(seconds=10)
        y_timestamp = int(time.mktime(yesterdayTime.timetuple()))
        records_num = 5  # grep 4 rec from each camera every 10sec

        channelIds = [
            "1000000$1$0$0"
        ]

        response = tasks_app.face_detection_api(c_timestamp, y_timestamp, records_num, channelIds)
        data_dict = {}
        group_detecion = 'N/A'
        if 'data' in response.json():
            data = response.json().get('data').get('pageData')
            if len(data) > 0:
                group_detecion = self.define_group(data)
                data_dict.update({'faceImageUrl': data[0]['faceImageUrl'],
                                  'pictureUrl': data[0]['pictureUrl'],
                                      'gender': data[0]['gender'],
                                      'age': data[0]['age']})

            data_dict.update({
                'group': group_detecion,
                'items_found': len(data)
            })

            # for dt in data:
            #     data_dict = {
            #         'code': dt['code'],
            #         'gender': dt['gender'],
            #         'age': dt['age'],
            #         'pictureUrl': dt['pictureUrl'],
            #         'faceImageUrl': dt['faceImageUrl'],
            #         'group': 'B'
            #     }

                # data_list.append(data_dict)

            print('item found and added to db ..{}'.format(len(data)))

        return data_dict









