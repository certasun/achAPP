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
import string
pp = pprint.PrettyPrinter(indent=2)
sf_token_updatedsan = 'MRkY20HRIBUTBbTM5U58eezT'
sf_user = 'nwayn@certasun.com'
sf_pass = 'Meerkat3250'
sf = Salesforce(sf_user +".updatedsan", sf_pass, sf_token_updatedsan, domain = 'test')
letters = list()
for i in range(len(string.ascii_lowercase)):
    letters.append(string.ascii_lowercase[i])
project_id_list = list()
for row in letters:
    query = sf.query("select Id from project__c where name LIKE '"+row+"%'")
    for row in query['records']:
        project_id_list.append(row['Id'])
pp.pprint(project_id_list)
print(len(project_id_list))
