
import boto3
import json
from datetime import timedelta
from datetime import datetime
from datetime import date
import os.path
from os import path


import uuid

import requests
import time

import csv

import base64
import requests
from requests.auth import HTTPDigestAuth

from flask import Flask , render_template
from flask import Response
from flask import request

domain_ip = "http://192.168.0.108/"
#domain_ip = "http://121.121.74.137:81/"

app = Flask(__name__)

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)


def get_avg_age(h, l):
    return (int(h) + int(l)) / 2


def create_csv_file(row):
    today = date.today()
    d3 = today.strftime("%d-%m-%Y")
    csv_file = 'report/report-'+ d3 +'.csv'
    if(path.exists(csv_file)):
        with open(csv_file, 'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
    else:
        with open(csv_file, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()


def get_images():
    try:
        import httplib
    except ImportError:
        import http.client as httplib

    httplib.HTTPConnection.debuglevel = 0

    url = domain_ip + "cgi-bin/snapshot.cgi?loginuse=admin&loginpas=admin123"
    image_base64 = ""
    img_filename = 'static/snapshot.jpg'
    try:
        image_base64 = requests.get(url, auth=HTTPDigestAuth('admin', 'admin123'),
                                    timeout=10).content

        unique_filename = str(uuid.uuid4())

        img_filename = 'static/' + unique_filename + '.jpg'  # I assume you have a way of picking unique filenames
        with open(img_filename, 'wb') as f:
            f.write(image_base64)

        return img_filename, image_base64

        # image_base64 = get_as_base64(response)
        # print(image_base64)
    except Exception as e:
        print(e)


def detect_faces():


    client=boto3.client('rekognition',region_name="ap-southeast-1", aws_access_key_id="AKIA4HFLH2NYASQL2SP6", 
    aws_secret_access_key = "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",
     )


    try:
        import httplib
    except ImportError:
        import http.client as httplib

    httplib.HTTPConnection.debuglevel = 0

    url = domain_ip + "cgi-bin/snapshot.cgi?loginuse=admin&loginpas=admin123"
    image_base64 = ""
    img_filename = 'static/snapshot.jpg'
    try:
        image_base64 = requests.get(url, auth=HTTPDigestAuth('admin', 'admin123'),
                                    timeout=30).content

        unique_filename = str(uuid.uuid4())

        img_filename = 'static/snapshot.jpg'  # I assume you have a way of picking unique filenames
        with open(img_filename, 'wb') as f:
            f.write(image_base64)



        # image_base64 = get_as_base64(response)
        # print(image_base64)
    except Exception as e:
        print(e)

    response = client.detect_faces(Image={'Bytes': image_base64}, Attributes=['ALL'])
    if 'FaceDetails' in response :
        gender_f = 0
        gender_m = 0

        age_groups = {
            '20-45': 0,
            '45+': 0
        }

        age_gender = {}

        number_of_faces = len(response['FaceDetails'])
        age_ranges = []
        age_gender_list = []


        #
        print('Detected faces for ' + str(number_of_faces))
        print(response)

        data_results = ''
        if number_of_faces > 0:
            for gen in response['FaceDetails']:


                # print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
                #       + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
                # print('Here are the other attributes:')
                # print(json.dumps(gen, indent=4, sort_keys=True))
                age = 0
                if 'AgeRange' in gen:
                    age = get_avg_age(gen['AgeRange']['High'], gen['AgeRange']['Low'])

                gender = 'N/A'
                if 'Gender' in gen:
                    gender = gen['Gender']['Value']

                data_results = data_results + json.dumps([gender, age], indent=4, sort_keys=True) + '\n'


                # for csv tsk
                age_gender_list.append(['', gender, age, ''])

                # define gender
                if gender == 'Male':
                    gender_m = gender_m + 1
                elif gender == 'Female':
                    gender_f = gender_f + 1

                # define age
                if 20 <= int(age) <= 45:
                    age_groups['20-45'] = age_groups['20-45'] + 1
                elif int(age) > 45:
                    age_groups['45+'] = age_groups['45+'] + 1

            if number_of_faces == 1:
                if gender_m == number_of_faces or gender_f == number_of_faces:  # male or female
                    if age_groups['20-45'] == number_of_faces:

                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        row = ['A', 'Gender', 'Age', dt_string]
                        row.append(age_gender_list)
                        create_csv_file(row)

                        return number_of_faces , "A" , img_filename, data_results

                    elif age_groups['45+'] == number_of_faces:

                        print(' one Face ')
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        row = ['C', 'Gender', 'Age', dt_string]
                        row.append(age_gender_list)
                        create_csv_file(row)

                        return number_of_faces, "C" , img_filename, data_results

            # check for 2 pax

            elif number_of_faces == 2:
                if (gender_m + gender_f == number_of_faces) and (gender_m is not 0) and (gender_f is not 0):
                    if age_groups['20-45'] == number_of_faces:

                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        row = ['B', 'Gender', 'Age', dt_string]
                        row.append(age_gender_list)
                        create_csv_file(row)

                        return number_of_faces, "B" , img_filename, data_results
                    elif age_groups['45+'] == number_of_faces:

                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        row = ['D', 'Gender', 'Age', dt_string]
                        row.append(age_gender_list)
                        create_csv_file(row)

                        return number_of_faces , "D", img_filename, data_results
                    
                    else :
                        return number_of_faces, "F" , img_filename, data_results

                else:  # 2 male or 2 female

                    # now = datetime.now()
                    # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    # row = ['F', 'Gender', 'Age', dt_string]
                    # row.append(age_gender_list)
                    # create_csv_file(row)

                    return number_of_faces, "F" , img_filename, data_results

            # check for froups
            elif number_of_faces > 2:

                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                row = ['E', 'Gender', 'Age', dt_string]
                row.append(age_gender_list)
                create_csv_file(row)

                return number_of_faces, "E", img_filename, data_results


        else :

            # now = datetime.now()
            # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            # row = ['F', 'Gender', 'Age', dt_string]
            # row.append(age_gender_list)
            # create_csv_file(row)

            return number_of_faces, "H", img_filename, data_results



        # now = datetime.now()
        # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        # row = ['F', 'Gender', 'Age', dt_string]
        # row.append(age_gender_list)
        # create_csv_file(row)

        return number_of_faces, "F", img_filename, data_results


@app.route("/data/test/group/demographics", methods=["GET"])
def demographics_group():
    photo='hlb-photos'
    bucket='bucket'
    group_detecion = 'F'
    items_count , group_detecion , images_code , data_dt = detect_faces()

    #dt = detect_faces()
    print("Faces detected: " + str(items_count))
    #js = {}
    js = json.dumps(
        {
        "success": "true",
        'group': str(group_detecion),
        'items_found' : int(items_count),
        'image' : str(images_code),
        'detection' : str(data_dt)

        }
    )

    resp = Response(js, status=200, mimetype='application/json')
    return resp



@app.route("/")
def hello():
   # return "Hello World!"
    return render_template('index.html')

if __name__ == "__main__":
    app.run("127.0.0.1", port=3030, debug=True)
