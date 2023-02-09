import re
import os
import json
from datetime import datetime
from flaskext.mysql import MySQL
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask import request
from flask_cors import CORS
from helpers.utils import create_json
import mysql.connector
from datetime import datetime


api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Content-Type'


class totalrealizedpnl(Resource):
    def post(self):
        request_json = request.get_json()
        
                
        result = create_json('success', record_list)
        return result
    
class totalrealizedpnl(Resource):
    def post(self):
        request_json = request.get_json()
        
          
        result = create_json('success', record_list)
        return result

class usersCount(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'users' not in request_json:
            return create_json('invalid request', "invalid request")
        conn = mysql.connect()
        cursor = conn.cursor()
        if request_json['users'].upper() == 'ALL':
            cursor.execute('''Select count(*) from tollow.user_info where active=%s''',
                       ('yes'))
        elif request_json['users'].upper() != 'ALL':
            cursor.execute('''Select count(*) from tollow.user_info where active=%s
                               and role=%s''',
                       ('yes',request_json['users']))
        
        
        record = cursor.fetchone()
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = []
        for rec in record:
            rec = (str(rec).replace(',', ''))
            rec = (str(rec).replace('((', '('))
            rec = (str(rec).replace('))', ')'))
            record_list.append(rec)
        result = create_json('success', record_list)
        return result



class schoolsDetails(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'schools' not in request_json:
            return create_json('invalid request as input', "invalid request")

        if request_json['schools'].upper() != 'ALL':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select 
                            school_name
                          , address
                          , city
                          , state
                          , country
                          , pincode
                          , contact_details
                          , active
                          , registration_page
                          , share_data
                          , retention 
                        from tollow.school_info ''',
                       )
        record = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = list(record)

        result = create_json('success', record_list)
        return result

class usersDetails(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'users' not in request_json:
            return create_json('invalid request', "invalid request")

        if request_json['users'].upper() != 'ALL':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select first_name
                                , last_name
                                , email 
                                , role
                                , school_name
                                , contact_number
                                , iep
                                , class_year
                                , assessment_request
                                , active 
                                from tollow.user_info''',
                       )
        record = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        if not record or record[0] == 0:
            return create_json('no records', "no records found")

        result = create_json('success', record)
        return result

class deleteUser(Resource):
    def post(self):

        request_json = request.get_json()
        if request_json and 'users' not in request_json:
            return create_json('invalid request', "invalid request")

        deleteusers = []
        deleteusers = request_json['users'].split(',')
        conn = mysql.connect()
        cursor = conn.cursor()

        for deluser in deleteusers:
            cursor.execute('''Delete from tollow.user_info where email = %s''', deluser)
            conn.commit()
            cursor.execute('''Select count(*) from tollow.user_info where email = %s''', deluser)
            record = cursor.fetchall()
            flag = 0
            if record or record[0] == 0:
                flag = 0
            else:
                flag = 1
                return create_json('internal error', "deletion process issue")
        result = create_json('success', 'record deleted')
        return result


api.add_resource(totalrealizedpnl, '/trpnl/')
api.add_resource(totalunrealizedpnl, '/tnpnl/')
api.add_resource(usersDetails, '/usersdetails/')
api.add_resource(usersCount, '/userscount/')
api.add_resource(deleteUser, '/deleteuser/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
    app.run(debug=True)