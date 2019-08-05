from flask import Flask, session, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import csv
import shutil
import os
import glob
from shutil import copyfile
import pprint
from decimal import Decimal
from simple_salesforce import Salesforce
import json
import time
pp = pprint.PrettyPrinter(indent=1)
application = Flask(__name__)
sf_user = 'nwayn@certasun.com'
sf_pass = 'Meerkat3250'
sf_consumer_key = '3MVG9vrJTfRxlfl7JrAPVnSBJscooRaBSEHaV0RU0Nh26ID0am9ZyHz5wQ99NhDv_uBXnw9lUy6rsXLa0byTU'
sf_consumerr_secret = 'F851D4F3EAA855D44D1A0B3FC543053B26FB333A212A444EDF13528CF755854D'
sf_token = 'eRwTg1P6YhnNSjEl1VqZGzCu6'
@application.route('/pvwatts', methods =['GET', 'POST'])
def pvwatts():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        proj_ID = request.json['id']
    sf = Salesforce(sf_user, sf_pass, sf_token)
    #query = sf.query("select ID from project__c where name = 'test'")
    #proj_ID = query['records'][0]['Id']
    query = sf.query("select Name, ID, (select MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+proj_ID+"')")
    street = query['records'][0]['Contacts']['records'][0]['MailingAddress']['street']
    city = query['records'][0]['Contacts']['records'][0]['MailingAddress']['city']
    zip = query['records'][0]['Contacts']['records'][0]['MailingAddress']['postalCode']
    state = query['records'][0]['Contacts']['records'][0]['MailingAddress']['state']
    address  = street + " " + city + " " + state + " " + zip
    query1 = sf.query("select Array_1_Tilt__c, Array_2_Tilt__c, Array_3_Tilt__c, Array_4_Tilt__c, Array_5_Tilt__c, Array_6_Tilt__c, Array_1_Modules__c, Array_2_Modules__c, Array_3_Modules__c, Array_4_Modules__c, Array_5_Modules__c, Array_6_Modules__c, Array_1_Module_DC_W__c, Array_2_Module_DC_W__c, Array_3_Module_DC_W__c, Array_4_Module_DC_W__c, Array_5_Module_DC_W__c, Array_6_Module_DC_W__c, Array_1_Azimuth__C, Array_2_Azimuth__c, Array_3_Azimuth__c, Array_4_Azimuth__c, Array_5_Azimuth__c, Array_6_Azimuth__c from project__c where ID = '"+proj_ID+"'")
    for i in range(6):
        if query1['records'][0]['Array_'+str(i+1)+'_Azimuth__c'] == None:
            size = i
            break
    if 'size' not in locals() and 'size' not in globals():
        size = 6
    solar_arrays = list()
    for i in range(size):
        solar_array_dict = {'Module DC W': query1['records'][0]['Array_'+str(i+1)+'_Module_DC_W__c'],
                            'Azimuth' : query1['records'][0]['Array_'+str(i+1)+'_Azimuth__c'],
                            'Tilt': query1['records'][0]['Array_'+str(i+1)+'_Tilt__c'],
                            'Modules': query1['records'][0]['Array_'+str(i+1)+"_Modules__c"]}
        solar_arrays.append(solar_array_dict)
    summation = 0
    pp.pprint(solar_arrays)
    for row in solar_arrays:
        tilt = row['Tilt']
        azimuth = row['Azimuth']
        DC_system_size = (row['Module DC W'] * row['Modules'])/1000
        with requests.Session() as s:
            params = {"address": address,
                        "api_key" : "c2jzpeSv7ZfiBwc2eCrEv3gdoAjkQA5lNhUsjVor",
                        "system_capacity" : DC_system_size,
                        "module_type" : 1,
                        "losses" : 14.08,
                        "array_type" : 1,
                        "tilt" : tilt,
                        "azimuth" : azimuth
                        }
            url = " https://developer.nrel.gov/api/pvwatts/v6.json"
            r = s.get(url, params = params)
            json =  r.json()
            ac_annual = json['outputs']['ac_annual']
            summation = summation + ac_annual
    sf.project__c.update(proj_ID, {'Year_1_PV_Watts_Prod_Est_kWh__c': summation})
    return '', 200



if __name__ == '__main__':
    application.run(debug=True)
