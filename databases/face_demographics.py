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




    def define_group(self, data):

        gender_f = 0
        gender_m = 0

        age_groups = {
            '20-45': 0,
            '45+': 0
        }

        age_gender = {}

        data_len = len(data)
        age_ranges = []

        for gen in data:

            age_ranges.append(gen['age'])

            # define gender
            if int(gen['gender']) == 1:
                gender_m = gender_m + 1
            elif int(gen['gender']) == 2:
                gender_f = gender_f + 1

            #define age
            if 20 <= int(gen['age']) <= 45:
                age_groups['20-45'] = age_groups['20-45'] + 1
            elif int(gen['age']) > 45:
                age_groups['45+'] = age_groups['45+'] + 1

        # Male

        print('F gender count ..')
        print(gender_f)
        print('M gender count ..')
        print(gender_m)

        number_of_faces = list(set(age_ranges))
        print('number of faces ')
        print(len(number_of_faces))

        # check for 1 pax

        if len(number_of_faces) == 1:
            if gender_m == data_len or gender_f == data_len:  #male or female
                    if age_groups['20-45'] == data_len:
                        print(' one Face ')
                        return "A"
                    elif age_groups['45+'] == data_len:
                            print(' one Face ')
                            return "C"

        # check for 2 pax

        elif len(number_of_faces) == 2:
            if (gender_m + gender_f == data_len) and (gender_m is not 0) and (gender_f is not 0 ):
                if age_groups['20-45'] == data_len:
                    return "B"
                elif age_groups['45+'] == data_len:
                    return "D"

            else:  # 2 male or 2 female
                return "F"

        # check for froups
        elif len(number_of_faces) > 2:
            if gender_m + gender_f == data_len: #group of diffrent gender kind male and female
                return "E"

            else :  # group of same kind of gender
                return "F"


    def get_summary_demographics_groups(self):

        tasks_app.login()

        # get last hour data
        currentTime = datetime.now()
        c_timestamp = int(time.mktime(currentTime.timetuple()))
        yesterdayTime = datetime.now() - timedelta(seconds=10)
        y_timestamp = int(time.mktime(yesterdayTime.timetuple()))
        records_num = 5  # grep 3 rec from each camera every 10sec

        channelIds = [
            "1000000$1$0$0"
        ]

        #response = tasks_app.face_detection_api(c_timestamp, y_timestamp, records_num, channelIds)
        response = tasks_app.face_detection_api(c_timestamp, y_timestamp , records_num, channelIds)

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









