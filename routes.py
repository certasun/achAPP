from flask import Flask, session, render_template, request, redirect, url_for, jsonify, abort, session
import stripe
import base64
import datetime
import time
from simple_salesforce import Salesforce
import pprint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
import json
from jinja2 import Environment, PackageLoader
import jinja2
import imghdr
import locale
import os
import pprint
import stripe
import requests
from email.utils import make_msgid
from flask_mail import Mail, Message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.headerregistry import Address
from email.message import EmailMessage
from email.mime.image import MIMEImage

application = Flask(__name__)
application.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde280ba245"
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 587,
    "MAIL_USE_TLS" : True,
    "MAIL_USERNAME" : 'wayno5650@gmail.com',
    "MAIL_PASSWORD" : 'Cush5656'
}
application.config.update(mail_settings)
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
pp = pprint.PrettyPrinter(indent=2)
stripe.api_key = 'sk_test_YfkekeTtUjhcaJEccJojqD6q'
app_settings ={
'DWOLLA_SECRET' : "hgSkU7DT6g0eOOdQAx9uDcxpofe52AdM3dzRnEMYUeWMA6awYn",
'DWOLLA_KEY' : 'MV2YxoL4xaazgVJk1bWpQgUeR6q0kCxg5lnipDL7YoJZdw8V0J',
'STRIPE_API_KEY' : stripe.api_key,
'PLAID_CLIENT_ID' : '5d07c2f19585840015a41676',
'PLAID_SECRET' : '3554c62d5732888c8099296d93cdfb',
'PLAID_SECRET_SAND' : '2ceef8e0abfc857bb801f7dffd06a9',
'PLAID_PUBLIC_KEY' : '89066d105257beb46bc1873e92467e',
'PLAID_BALANCE' : 10000,
'PLAID_ENV' : PLAID_ENV,
'DWOLLA_ACCOUNT_FUNDING_SOOURCE_ID' : '94e5a2f5-0bb3-4cf6-9e32-8081be3040c5',
'SF-USER' : 'nwayn@certasun.com',
'SF-PASS' : 'Meerkat3250',
'SF-TOKEN' : 'LXaurDjGHUkmaAtU4fHwySPL',
'DOWN_PAYMENT_CONST' : 'Down Payment',
'PERMIT_PAYMENT_CONST' : 'Permit Payment',
'FINAL_PAYMENT_CONST' : "Final Payment",
'DUE_STATUS' : 'Due',
'NOT_DUE_STATUS' : 'Not Due',
'IN_FLIGHT_STATUS' : 'In Flight',
'RECEIVED_STATUS' : 'Received',
'N/A_STATUS' : 'N/A',
'GMAIL_ADDRESS' : 'wayno5650@gmail.com',
'GMAIL_PASSWORD' : 'Cush5656',
'OUTLOOK_ADDRESS' : "nathan@certasun.com",
'SMTP_USERNAME' : "AKIATZ6Y4YOTZWCBF56T",
'SMTP_PASSWORD' : "BItZz8Wcas9aFuZcZnRh8IVRlLXpKdl4ardA8UXOsCmr",
'AWS_SES_ENDPOINT' : "email-smtp.us-east-1.amazonaws.com",
'DWOLLA_UNVERIFIED_LIMIT' : 4000,
'DWOLLA_VERIFIED_LIMIT' : 30000,
}
sf_sandbox_token = 'LXaurDjGHUkmaAtU4fHwySPL'
sf_user_sand_update = 'nwayn@certasun.com.updatedSan'
sf_update_san_token = 'MRkY20HRIBUTBbTM5U58eezT'

class nameForm(FlaskForm):
    name = StringField('Email')
    submit = SubmitField('SUBMIT')

class retryForm(FlaskForm):
    firstName = StringField('FirstName')
    lastName = StringField('lastName')
    street_address = StringField('Street Address')
    city = StringField('City')
    state_Code = StringField('State Code')
    zip = StringField('ZIP Code')
    retry_email = StringField('Email')
    DOB = StringField('DOB (YYYY-MM-DD)')
    SSN = PasswordField('SSN (Full 9 Digits)')
    submit = SubmitField('SUBMIT')

class decodeForm(FlaskForm):
    hash = PasswordField('hash')
    submit = SubmitField('submit')

class verificationForm(FlaskForm):
    SSN = PasswordField('Last 4 of SSN')
    DOB = DateField('DOB (YYYY-MM-DD)')
    submit = SubmitField('Submit')

class ACCOUNT:
    def __init__(self, name, fname, lname):
        self.name = name
        self.fname = fname
        self.lname = lname
        self.dp = 0
        self.pp = 0
        self.fp = 0
        self.dpSTAT = ""
        self.ppSTAT = ""
        self.fpSTAT = ""
        self.ID = 0
        self.duePayment = ""
        self.chargeAmount = 0
    def getnextpayment(self):
        if self.duePayment == app_settings['DOWN_PAYMENT_CONST']:
            self.chargeAmount = self.dp
            return self.dp
        if self.duePayment == app_settings['PERMIT_PAYMENT_CONST']:
            self.chargeAmount = self.pp
            return self.pp
        if self.duePayment == app_settings['FINAL_PAYMENT_CONST']:
            self.chargeAmount = self.fp
            return self.fp
        return 0

    def toJSON(self):
        return self.__dict__

    def getDuePayment(self):
        if self.dpSTAT == app_settings['DUE_STATUS'] or self.dpSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['DOWN_PAYMENT_CONST']
            return app_settings['DOWN_PAYMENT_CONST']
        elif self.ppSTAT == app_settings['DUE_STATUS'] or self.ppSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['PERMIT_PAYMENT_CONST']
            return app_settings['PERMIT_PAYMENT_CONST']
        elif self.fpSTAT == app_settings['DUE_STATUS'] or self.fpSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['FINAL_PAYMENT_CONST']
            return app_settings['FINAL_PAYMENT_CONST']
        else:
            self.duePayment = "N/A"
        return "N/A"

def toOBJ(myobj):
        OBJ = ACCOUNT(myobj['name'], myobj['fname'], myobj['lname'])
        OBJ.dp = myobj['dp']
        OBJ.pp = myobj['pp']
        OBJ.fp = myobj['fp']
        OBJ.dpSTAT = myobj['dpSTAT']
        OBJ.ppSTAT = myobj['ppSTAT']
        OBJ.fpSTAT = myobj['fpSTAT']
        OBJ.ID = myobj['ID']
        OBJ.duePayment = myobj['duePayment']
        OBJ.chargeAmount = myobj['chargeAmount']
        return OBJ
# takes in the status code for payments from SF and returns a more consumer friendly string to display on the front end
def setFrontEndStatus(stat):
    if stat == app_settings['DUE_STATUS']:
        return app_settings['DUE_STATUS']
    elif stat == app_settings['NOT_DUE_STATUS']:
        return ' '
    elif stat == app_settings['IN_FLIGHT_STATUS']:
        return "Pending"
    elif stat == app_settings['RECEIVED_STATUS']:
        return 'Paid'
    elif stat == app_settings['N/A_STATUS']:
        return app_settings['N/A_STATUS']
    else:
        return " "

@application.route('/pvwatts', methods =['GET', 'POST'])
def pvwatts():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        proj_ID = request.json['id']
        print(proj_ID)
    sf = Salesforce(sf_user_sand_update, app_settings['SF-PASS'], sf_update_san_token, domain = 'test')
    query = sf.query("select Name, ID, (select MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+proj_ID+"')")
    pp.pprint(query)
    if query['totalSize'] == 0:
        return '', 300
    if query['records'][0]['Contacts']['totalSize'] == 0:
        return '', 404
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
    #sf.project__c.update(proj_ID, {'Year_1_PV_Watts_Prod_Est_kWh__c': summation})
    print(summation)
    return '', 200


@application.route('/displayEmail/<id>', methods = ['GET', 'POST'])
def displayemail(id):

        sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
        # get the email belonging to the contact for whom the project is for
        contact_query = sf.query("select Name, ID, (select name, email, MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+id+"')")
        #link that will be sent in the email in order for the customer to go to payment portal
        email_link = "https://certasunpay.com/linkwithid/" + id
        templateLoader = jinja2.FileSystemLoader(searchpath = "/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        ### get the rest of the data from the project in order to format the templated email
        query = sf.query("select id, Name, Cash_Down_Pmt_Status__c, Cash_Down_Pmt__c, Cash_Permit_Pmt_Status__c, Permit_Pmt__c, Cash_Final_Pmt_Status__c, Cash_final_Pmt__c from Project__c where ID =  '"+id+"'")
        #project down payment:
        p_down = query['records'][0]['Cash_Down_Pmt__c']
        #project down payment status:
        p_down_stat = query['records'][0]['Cash_Down_Pmt_Status__c']
        #project permit payment:
        p_permit = query['records'][0]['Permit_Pmt__c']
        #project permit payment status:
        p_permit_stat = query['records'][0]['Cash_Permit_Pmt_Status__c']
        #project final payment:
        p_final = query['records'][0]['Cash_Final_Pmt__c']
        #project final payment status:
        p_final_stat = query['records'][0]['Cash_Final_Pmt_Status__c']
        #concatonate a string to show the customers address
        address = str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['street']) + " " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['city']) + ", " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['state'])
        #Name of contact whom project belongs to:
        contact_name = contact_query['records'][0]['Contacts']['records'][0]['Name']
        #split the contact name to get first and last seperate
        contact_name_list = contact_name.split()
        #create an ACCOUNT object for this project
        email_recipient_account = ACCOUNT(contact_query['records'][0]['Name'], contact_name_list[0], contact_name_list[1])
        #set the objects down payment:
        email_recipient_account.dp = p_down
        #set objects down payment status:
        email_recipient_account.dpSTAT = setFrontEndStatus(p_down_stat)
        #set objects permit payment:
        email_recipient_account.pp = p_permit
        #set objects permit payment status:
        email_recipient_account.ppSTAT = setFrontEndStatus(p_permit_stat)
        #set objects final payment:
        email_recipient_account.fp = p_final
        #set objects final payment status:
        email_recipient_account.fpSTAT = setFrontEndStatus(p_final_stat)
        #use getDuePayment method to find out which payment will need to be paid next with logic in that method
        duepayment = email_recipient_account.getDuePayment()
        #use getnextpayment to get the value of the duepayment
        next_payment = email_recipient_account.getnextpayment()
        #locale is used to format currency
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
        #format the next_payment from a float to a currency string
        next_payment = locale.currency(next_payment)
        #### create id's to reference images that will be embedded in email
        logoImage_cid = make_msgid()
        bg1Image_cid = make_msgid()
        facebook_cid = make_msgid()
        twitter_cid = make_msgid()
        ig_cid = make_msgid()
        #############
        #create the templated email
        html = render_template('emailtemplate1.html', name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1]) #, twitter_cid = twitter_cid[1:-1], ig_cid = ig_cid[1:-1])
        #instantiate an EmailMessage OBject
        msg = EmailMessage()
        #Email's subject:
        msg['Subject'] = 'Pay Certasun'
        #Email address message will be sent from
        msg['From'] = app_settings['OUTLOOK_ADDRESS']#mail_settings['MAIL_USERNAME']
            ############# change back but for testing send to my email ###################
        #Address Email will be sent to
        msg['To'] = "wayno5650@gmail.com"#email
        #############################################################################
        #Email messages preamble
        msg.preamble = "Certasun"
        #set the plain text as an empty string
        msg.set_content("")
        #set the templated html of the message
        msg.add_alternative(html, subtype = 'html')
        ############# Embed the images into the email msg###################
        with open('static/img/CertasunLogo.png', 'rb') as fp:
            msg.get_payload()[1].add_related(fp.read(), 'image','png',cid=logoImage_cid)
        with open('static/img/bg1.png', 'rb') as fp:
            msg.get_payload()[1].add_related(fp.read(), 'image', 'png', cid = bg1Image_cid)
        with open('static/img/free_ico_facebook.jpg', 'rb') as fp:
            msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = facebook_cid)

        return render_template('emailtemplate1.html', name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1])

@application.route('/displayEmail2/<id>', methods = ['GET', 'POST'])
def displayemail2(id):

        sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
        # get the email belonging to the contact for whom the project is for
        contact_query = sf.query("select Name, ID, (select name, email, MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+id+"')")
        #link that will be sent in the email in order for the customer to go to payment portal
        email_link = "https://certasunpay.com/linkwithid/" + id
        templateLoader = jinja2.FileSystemLoader(searchpath = "/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        ### get the rest of the data from the project in order to format the templated email
        query = sf.query("select id, Name, Cash_Down_Pmt_Status__c, Cash_Down_Pmt__c, Cash_Permit_Pmt_Status__c, Permit_Pmt__c, Cash_Final_Pmt_Status__c, Cash_final_Pmt__c from Project__c where ID =  '"+id+"'")
        #project down payment:
        p_down = query['records'][0]['Cash_Down_Pmt__c']
        #project down payment status:
        p_down_stat = query['records'][0]['Cash_Down_Pmt_Status__c']
        #project permit payment:
        p_permit = query['records'][0]['Permit_Pmt__c']
        #project permit payment status:
        p_permit_stat = query['records'][0]['Cash_Permit_Pmt_Status__c']
        #project final payment:
        p_final = query['records'][0]['Cash_Final_Pmt__c']
        #project final payment status:
        p_final_stat = query['records'][0]['Cash_Final_Pmt_Status__c']
        #concatonate a string to show the customers address
        address = str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['street']) + " " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['city']) + ", " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['state'])
        #Name of contact whom project belongs to:
        contact_name = contact_query['records'][0]['Contacts']['records'][0]['Name']
        #split the contact name to get first and last seperate
        contact_name_list = contact_name.split()
        #create an ACCOUNT object for this project
        email_recipient_account = ACCOUNT(contact_query['records'][0]['Name'], contact_name_list[0], contact_name_list[1])
        #set the objects down payment:
        email_recipient_account.dp = p_down
        #set objects down payment status:
        email_recipient_account.dpSTAT = setFrontEndStatus(p_down_stat)
        #set objects permit payment:
        email_recipient_account.pp = p_permit
        #set objects permit payment status:
        email_recipient_account.ppSTAT = setFrontEndStatus(p_permit_stat)
        #set objects final payment:
        email_recipient_account.fp = p_final
        #set objects final payment status:
        email_recipient_account.fpSTAT = setFrontEndStatus(p_final_stat)
        #use getDuePayment method to find out which payment will need to be paid next with logic in that method
        duepayment = email_recipient_account.getDuePayment()
        #use getnextpayment to get the value of the duepayment
        next_payment = email_recipient_account.getnextpayment()
        #locale is used to format currency
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
        #format the next_payment from a float to a currency string
        next_payment = locale.currency(next_payment)
        #### create id's to reference images that will be embedded in email
        logoImage_cid = make_msgid()
        bg1Image_cid = make_msgid()
        facebook_cid = make_msgid()
        twitter_cid = make_msgid()
        ig_cid = make_msgid()
        #############
        #create the templated email
        html = render_template('emailtemplate1.html', name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1]) #, twitter_cid = twitter_cid[1:-1], ig_cid = ig_cid[1:-1])
        display_html = render_template("email2.html",  name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address)
        with open("my_new_file.html", "w") as fh:
            fh.write(display_html)
        os.system('my_new_file.html')
        my_input = input('Do you want to send this email (Y/N)')
        if(my_input == 'Y' or my_input = 'y'):
            #instantiate an EmailMessage OBject
            msg = EmailMessage()
            #Email's subject:
            msg['Subject'] = 'Pay Certasun'
            #Email address message will be sent from
            msg['From'] = 'IT@certasun.com'#mail_settings['MAIL_USERNAME']
                ############# change back but for testing send to my email ###################
            #Address Email will be sent to
            msg['To'] = "wayno5650@gmail.com"#email
            #############################################################################
            #Email messages preamble
            msg.preamble = "Certasun"
            #set the plain text as an empty string
            msg.set_content("")
            #set the templated html of the message
            msg.add_alternative(html, subtype = 'html')
            ############# Embed the images into the email msg###################
            with open('static/img/CertasunLogo.png', 'rb') as fp:
                msg.get_payload()[1].add_related(fp.read(), 'image','png',cid=logoImage_cid)
            with open('static/img/bg1.png', 'rb') as fp:
                msg.get_payload()[1].add_related(fp.read(), 'image', 'png', cid = bg1Image_cid)
            with open('static/img/free_ico_facebook.jpg', 'rb') as fp:
                msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = facebook_cid)
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 0)
            smtp.ehlo()
            #start tls which means message will be encrypted
            #smtp.starttls()
            #login to the AWS SES account
            smtp.login('IT@certasun.com', 'GoSolar1')
            #send the message, first parameter is who it is from, 2nd is who is is two and the thirsd is the content of the message
            smtp.sendmail("nathan@certasun.com", 'wayno5650@gmail.com', msg.as_string())
            #shutdown the connection to the smtp server
            smtp.quit()
        return render_template('email2.html', name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1])

#route for the main landing page where user may enter their email to access their payment portal
@application.route('/', methods = ['GET', "POST"])
@application.route('/landingpagelayout', methods = ['GET', 'POST'])
def landing_page():
    #open an API connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #instantiate the form that will be displayed on the PAGE
    #in this case the form will have 1 inpute which will be the email
    #and a submit button
    form = nameForm()
    #if the form is validated after submit button is hit this statement will execute
    if form.validate_on_submit():
        #clear all session variables so their are no data integrity issues
        session.clear()
        #get the email that was entered into the form
        email = form.name.data
        #query salesforce for the project associated with the contact that holds that email
        query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
        #statement is executed if there is no contact with that email or the contact with that email has no associated projects
        if query['totalSize'] == 0 or query['records'][0]['Projects__r'] == None:
            #redirect them to the invalidName page so a error message will appear telling them that the email is invalid and allowingg them to re enter their email
            return redirect(url_for('InvalidName'))
        #this statement will execute if the contact that holds the entered email has more than one project associated with it
        elif query['records'][0]['Projects__r']['totalSize'] > 1:
            #set a session variable to hold the email
            session['email'] = email
            #redirect to a page that gives a list of project names associated with that email so that the user will be able to chose which project they are looking to make a payment for
            return redirect(url_for('multipleRecords', email = email))
        #If the contact that holds that email has exactly one project associated with it this statement will execute
        elif query['records'][0]['Projects__r']['totalSize'] == 1:
            #again set a session variable to hold the email
            session['email'] = email
            #redirect user to method that will get all the info on the project and then display the user their payment portal
            return redirect(url_for('passObjID', id = query['records'][0]['Projects__r']['records'][0]['Id']))
    #index3.html is the landing page html document
    return render_template('index3.html', form = form)

#CHECKS TRANSFER STATUS AND REDIRECTS TO CORRECT PAGE BASED ON TRANSFER STATUS
@application.route('/thanks')
def thanks():
    #instatiate a connection to salesforce API
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    return render_template('newEnd.html', big_message = "Thank You")

@application.route('/failed')
def failed():
    return render_template('failed.html')

#CAN BE ACCESSED EITHER FROM A LINK OR FROM THE startPage
#FIRST WILL CLEAR THE SESSION FOR DATA INTEGRITY
#WILL THEN GET THE CONTACT NAME FROM SALESFORCE BY USING THE PROJECT ID PROVIDED
#takes in one parameter whihc is the project id
@application.route('/linkwithid/<id>', methods = ['GET', "POST"])
def passObjID(id):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    session.clear()
    #instantitate the form
    form = verificationForm()
    # set a session variable to store the project ID
    session['proj_ID'] = id
    #query salesforce for the ID of the Account that is associated with the project
    contact_query = sf.query("select contact_first_name__c, contact_last_name__c, Name, ID, (select name, email, MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+id+"')")
    # this statement will execute if there is no account associated with that project
    if contact_query['totalSize'] == 0:
        #they will be redirected to a page with an error message saying that the email does exist this
        #really should never occur the only way this would occur is if someone deleted either the project
        # or cantact in salesforce after the email was sent to them which would result in a dead link
        #but instead it would now redirect them to a page where they can enter their email to find their payment portal
        return(redirect(url_for('InvalidName')))
    #set a local variable to hold the account ID that was returned by the salesforce query
    accountID = contact_query['records'][0]['Id']
    # set a local variable to hold email that was sent back from salesforce
    email = contact_query['records'][0]['Contacts']['records'][0]['Email']
    #set a session variable for that same email that was sent back by salesforce
    session['email'] = email
    #set a local variable for the accout name that was returned by salesforce
    A_NAME = contact_query['records'][0]['Name']
    #set a session variable for the same account name that was returned by salesforce
    session['name'] = A_NAME
    #set a local variable for the customers first name that was returned by salesforce
    first_name = contact_query['records'][0]['Contact_First_Name__c']
    #set a local variable for the customerss last name that was returned by salesforce
    last_name = contact_query['records'][0]['Contact_Last_Name__c']
    #if for some reason the account in salesforce didnt have a last name
    if last_name == None:
        lastname = "lastname"
    #call the runqueries method that takes in a the account name, customer first name, customer last name, and the project ID and will return an ACCOUNT object
    passAccount = runQueriesID(A_NAME, first_name, last_name, id)
    #set a session variable for the data inside the ACCOUNT object that was just instantiated above by converting all the data inside the object to a json
    session['passAccount'] = passAccount.toJSON()
    #setting error codes to default settings
    session['Validation_Error'] = 'No Error'
    session['transfer_status'] = "BLANK"
        #make sure Account OBJ exists
    if passAccount:
        #get the value for the charge and set as a local variable
        send_payment = passAccount.getnextpayment()
        #set a session variable for the next payment
        session['send_payment'] = send_payment
        #get additional data from sf to show on page
        name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" +email+ "%'")
        #set a local variable for the city
        a_city = name_address['records'][0]['MailingAddress']['city']
        #set a local variable for the state
        a_state = name_address['records'][0]['MailingAddress']['state']
        #set a local variable for the street address
        a_street = name_address['records'][0]['MailingAddress']['street']
        #set a local variable for the zip code
        a_zip = name_address['records'][0]['MailingAddress']['postalCode']
        #create a json to hold all of the address information so that it can be passed to the front end to be rendered much easier
        location = {
        'city' : a_city,
        'state' : a_state,
        'street' : a_street,
        'zip' : a_zip
        }
        #we are going to check if the payment that needs to be made next is the downpayment and if so we want to waive the credit card convienience fee so we will set a
        # local variable to be sent to the front end to tell whether we need to charge the credit card convienience fee or not
        if passAccount.duePayment == 'Down Payment':
            #using either a one or a zero because was having issues in front end logic determining equality of strings
            charge_fee = 0
        else:
            charge_fee = 1
        return render_template('ach-credit.html',charge_fee = charge_fee, accountobj = passAccount, payment = send_payment, email = email, location = location)
    else:
         return redirect(url_for('newStart'))

@application.route('/ach', methods = ['POST'])
def ach_handler():
    routing_num = request.form['routing']
    b_account_number = request.form['banking']
    proj_ID = request.form['proj_ID']
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    sf.project__c.update(proj_ID, {'Bank_Account_Number__c': b_account_number})
    sf.project__c.update(proj_ID, {'Routing_Number__c' : routing_num})
    return redirect(url_for('thanks'))

#stripe credit card charge implementation
@application.route('/charge', methods = ['GET', 'POST'])
def credit_handler():
    #get the stripe token
    token = request.form['stripeToken']
    #create a charge with the data from the form
    charge = stripe.Charge.create(
        #amount stripe will charge the credit card
        amount=request.form['amount'],
        #currency of the amount
        currency='usd',
        #description of the charge
        description=request.form['description'],
        #token from stripe
        source=token,
        #metadata added so we can retrieve customer information from webhook events and send email upon failure or completion if we so pleae
        metadata = {'email': request.form['email'],
                    #paytype is the payment type for example down payment, permit payment, or final payment
                    'payType':request.form['payType'],
                    #project ID in salesforce
                    'proj_id' : request.form['proj_ID']}
    )
    #this statement will only execute if stripe returns a status of paid whcih means the transaction was successful
    if charge['paid'] == True:
        #get the project id from the metadata of the stripe charge
        proj_ID = charge['metadata']['proj_id']
        #change the payment status in salesforce for that particular payment for instance down payment that is held in the response['paytype'] metadata
        # now we are changing it to in flight and recieved from a webhook event but may just want to change it directly to recieved here as I believe this means
        #charge was successful
        change_payment_status_in_sf(request.form['payType'], proj_ID, "In Flight")
        #set a session variable to stripe_paid_true this is reference in the thanks() method and is used in the logic so it knows
        # to display the thank you page instead of the error page because the payment was successful if the program made it to this line
        session['transfer_status'] = 'stripe_paid_true'
        #redirect the customer to the thanks page to tell them that the payment is pending
    return redirect(url_for('thanks'))

#this method is called to run queries in salesforce on a given project and return an ACCOUNT object with all relevant DATA
# this method had 4 parameters
    #1: name = the name of the account in SALESFORCE
    #2: fname = the first name of the contact in SALESFORCE
    #3: lname = the last name of the contact in SALESFORCE
    #4: id = the project id from SALESFORCE
def runQueriesID(name, fname, lname, id):
    #instantiate a connection to SALESFORCE
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    # create an ACCOUNT object from the parameters
    thisAccount = ACCOUNT(name, fname, lname)
    #query salesforce for the payment information on this project
    query = sf.query("select Name, id, Cash_Down_pmt__c, Cash_Down_Pmt_Status__c, Permit_pmt__C, Cash_Permit_Pmt_Status__c, Cash_final_Pmt__c, Cash_final_pmt_status__c from Project__c where id = '" + id + "'")
    #set the rest of the varicables for the ACCOUNT object ###########################################
    thisAccount.ID = query['records'][0]['Id']
    thisAccount.dp = query['records'][0]['Cash_Down_Pmt__c']
    thisAccount.dpSTAT = setFrontEndStatus(query['records'][0]['Cash_Down_Pmt_Status__c'])
    thisAccount.pp = query['records'][0]['Permit_Pmt__c']
    thisAccount.ppSTAT = setFrontEndStatus(query['records'][0]['Cash_Permit_Pmt_Status__c'])
    thisAccount.fp = query['records'][0]['Cash_Final_Pmt__c']
    thisAccount.fpSTAT = setFrontEndStatus(query['records'][0]['Cash_Final_Pmt_Status__c'])
    ####################################################################################################
    #want to find which of the three possible payments needs to be paid next and set it as the next duepayment
    if thisAccount.dpSTAT == app_settings['DUE_STATUS'] or thisAccount.dpSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.dpSTAT == ' ':
        thisAccount.duePayment = app_settings['DOWN_PAYMENT_CONST']
        return thisAccount
    elif thisAccount.ppSTAT == app_settings['DUE_STATUS'] or thisAccount.ppSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.ppSTAT == ' ':
        thisAccount.duePayment = app_settings['PERMIT_PAYMENT_CONST']
        return thisAccount
    elif thisAccount.fpSTAT == app_settings['DUE_STATUS'] or thisAccount.fpSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.fpSTAT == ' ':
        thisAccount.duePayment = app_settings['FINAL_PAYMENT_CONST']
        return thisAccount
    else:
        thisAccount.duePayment = "NA"
    return thisAccount

#invalidEmail was given ask for email
@application.route('/InvalidName', methods = ['GET', 'POST'])
def InvalidName():
    #instantiate a connetion to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #instantiate the form
    thisform = nameForm()
    #this statement will run if the form validates after the submit button is pressed
    if thisform.validate_on_submit():
        #data taken from the input in the form
        email = thisform.name.data
        #query salesforce in order to get the project Id and some account information
        query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
        #if there is either no contact associated with that email or no project associated with the contact that holds that email this statement will run
        if query['totalSize'] == 0 or query['records'][0]['Projects__r'] == None:
            #this will redirect the user to the same form and an error message will be displayed saying the email was invalid and they will be prompted for email again
            return redirect(url_for('InvalidName'))
        #this statement will run only when there are more than 1 projects associated with the contact that holds that email
        elif query['records'][0]['Projects__r']['totalSize'] > 1:
            #set a session variable to hold the email address
            session['email'] = email
            #redirect to a page that lists all the projects under than contact so customer can choose
            return redirect(url_for('multipleRecords', email = email, query = query))
        #this statement will run if there is exactly one project associated with that email address
        elif query['records'][0]['Projects__r']['totalSize'] == 1:
            #set a session variable to hold that email
            session['email'] = email
            #you successfully have a project Id now so you can move on tp the payment portal for that ID
            return redirect(url_for('passObjID', id = query['records'][0]['Projects__r']['records'][0]['Id']))
    return render_template('Invalid.html', form = thisform)

#more than one project exists for the given contact customer must choose which project they would like to pay for
@application.route('/multipleRecords/<email>')
def multipleRecords(email):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'] , domain = 'test')
    #query salesfore for the account and projects data associated with that contact
    query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
    #instantiate a list to hold projects
    accountList = list()
    #for loop that will go through all of the projects and create dictionaries holding there ID's and names and append them to the above list so they may be sent to the front end to be displayed to the customer
    for i in range(query['records'][0]['Projects__r']['totalSize']):
        account_dict = {'Name':query['records'][0]['Projects__r']['records'][i]['Name'], 'ID': query['records'][0]['Projects__r']['records'][i]['Id']}
        accountList.append(account_dict)
    return render_template('multipleRecordsNew.html', accounts = accountList)

#this method runs when we were not able to verify the customer based of the information we got from salesforce and from the validation form
# we dont want to provide the customer with an error message in order to ensure a better user flow because of this we tell them payment is pendign and
# we retrieve their bank account and routing numbers from plaid and put them in salesforce so we can run the transfer manually
def customer_not_verified_encode_upload_send(customer_create_request_body):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +customer_create_request_body['email']+ "')")
    name = query['records'][0]['Name']
    proj_ID = query['records'][0]['Projects__r']['records'][0]['Id']
    # call the plaid api auth endpoint to retrieve the user bank account number and routing number
    auth_response = client.Auth.get(session['access_token'])
    #this for loop is used so that we can go through all bank accounts associated with the login the user entered and match it
    # with the accocunt they clicked in the GUI so we can get the correct account number
    for i in range(len(auth_response['numbers']['ach'])):
        #this statement will only run when the accountID matches the account in the plaid auth response
        if auth_response['numbers']['ach'][i]['account_id'] == session['ACCOUNT_ID']:
            #set local variable for bank account number
            account_num = auth_response['numbers']['ach'][i]['account']
            #set local variable for vank routing number
            routing_num = auth_response['numbers']['ach'][i]['routing']
            #put the bank accounts routing number into salesforce in the encrypted field created for the account number
            sf.project__c.update(proj_ID, {'Bank_Account_Number__c': account_num})
            #put the routing number into salesforce in the encrypted field created for the routing number
            sf.project__c.update(proj_ID, {'Routing_Number__c': routing_num})
            #this will send an email to the address in the first parameter including information about the customer who could not be verified, this works
            # as an alert that the payment must be done MANUALLY
            email_sender("nathan@certasun.com", "verification fail", name + " proj ID: " + str(proj_ID), 0)
    return

#This method is called by the front end to see if there were any errors in the payment process
# if there were the customer will be redirected to the error screen with an error message
# otherwise they will be pushed to the thank you payment pending screen
@application.route('/sessVars')
def getSessVars():
    if session['Validation_Error'] != 'No Error':
        return session['Validation_Error']
    else:
        return 'No Error'

#takes an email and returns the corresponding project ID queried from salesforce
def get_proj_from_sf(email):
    #instantiate salesforce connection
    sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
    #query salesforce databse for proj_ID
    query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '"+email+"')")
    #set a local variable for the project ID quiered from salesforce to be returned by this method
    proj_ID = query['records'][0]['Projects__r']['records'][0]['Id']
    return proj_ID

#takes in a project ID and a payment type and status and changes the payment status for that payment type for that project to the input
def change_payment_status_in_sf(payment_type, proj_ID, change_to):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #this statement will run if the payment status that must be changed which is the parament: payment_type
    # is the down payment
    if payment_type == app_settings['DOWN_PAYMENT_CONST']:
        #change the value for the down payment status equal to the parameter: change_to
        sf.project__c.update(proj_ID, {'Cash_Down_Pmt_Status__c': change_to})
    #this statement will only run if the payment type taken in as a parameter is equal to PERMIT PAYMENT
    elif payment_type == app_settings['PERMIT_PAYMENT_CONST']:
        #change the value of the permit payment status to the parameter change_to
        sf.project__c.update(proj_ID, {'Cash_Permit_Pmt_Status__c': change_to})
    #this statement will only run if the parameter payment_tpye: is equal to FINAL PAYMENT
    elif payment_type == app_settings['FINAL_PAYMENT_CONST']:
        #change the value of the permit final payment status equal to the parameter change_to
        sf.project__c.update(proj_ID, {'Cash_Final_Pmt_Status__c': change_to})
    else:
        #if the payment type parameter was not equal to any of the available options then ERROR will be returned
        return "ERROR"
    #otherwise PASS will be returned in order to indicate a successful sf update
    return "PASS"

if __name__ == '__main__':
    application.run(debug=True)
