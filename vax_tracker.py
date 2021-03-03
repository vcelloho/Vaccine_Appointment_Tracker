# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:13:48 2021

@author: jho
"""

  
from selenium import webdriver
import time
import smtplib
import random
from datetime import datetime, timedelta
import pandas as pd
import requests
import tweepy
from shutil import copyfile
import settings



def tweet(message):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(settings.TwitterConsumerKey, settings.TwitterConsumerSecret)
    auth.set_access_token(settings.TwitterAccessToken, settings.TwitterAccessTokenSecret)    
    # Create API object
    api = tweepy.API(auth)
    # Create a tweet
    api.update_status(message)


def send(message):
    carriers = {
    'att':    '@mms.att.net',
    'tmobile':' @tmomail.net',
    'verizon':  '@vtext.com',
    'sprint':   '@page.nextel.com'
    }
    # Replace the number with your own, or consider using an argument\dict for multiple people.
    to_number = '5555555555{}'.format(carriers['att'])
    auth = (settings.EmailAddress, settings.EmailPassword)

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP(settings.EmailSTMPAddress, settings.EmailSTMPPort )
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail( auth[0], to_number, message)
def gettime():
    now = datetime.now()
    return(now.strftime("%D %H:%M:%S"))
def getdate():
    now = datetime.now()
    return(now.strftime("%y%m%d%H%M%S"))

def archivehtml(Location,arch_type):
    if(arch_type=="false positive"):
        copyfile('/home/pi/'+Location+'.html', '/mnt/Dioscuri/Not Synced/False Positive Archive/'+getdate() +Location+'.html')
    if(arch_type=="found vaccine"):
        copyfile('/home/pi/'+Location+'.html', '/mnt/Dioscuri/Not Synced/Vaccine Site Archive/'+getdate() +Location+'.html')

def get_website(URL,Location):
    #URL="https://uma.force.com/covidtesting/s/vaccination"
    #Location="UMass"
    if(str(requests.get(URL))=="<Response [200]>"):
        ff = webdriver.Chrome('/usr/bin/chromedriver')
        ff.get(URL)
        time.sleep(30)
        with open('/home/pi/'+Location+'.html', 'w') as f:
            f.write(ff.page_source)
        ff.quit()
        f.close()
    else:
        print("FAILED: " + URL)
def check_for_text(Trigger_Text, Location):
    with open('/home/pi/'+Location+'.html') as f:
        if Trigger_Text in f.read():
            return True
        else:
            return False
def check_status(Trigger_Text, Location, URL):  
    #Trigger_Text="Anything"
    #Location="Baystate Health"
    #URL="Anything"
    print("Checking " + Location)
    if(check_for_text(Trigger_Text,Location)):
        print(gettime() + " No Appointments")
        return False
    else:
        print(gettime() + " Vaccine may be available")
        num_appointments=count_appointments(Location, URL)
        if(num_appointments==0):
            print(gettime() + " No Appointments")
        elif(num_appointments==-1):
            tweet("Vaccine may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        else:
            tweet(str(num_appointments) + " vaccine appointments may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        archivehtml(Location, "found vaccine")
        return True
        
def catch_false_positive(Location):
    fp_list=pd.read_csv("/mnt/Dioscuri/Not Synced/False_Positive_Checks.csv")
    for index,row in fp_list.iterrows():
        if(check_for_text(row['False_Positives'],Location)):
            print(gettime() + " False Positive " + Location)
            archivehtml(Location, "false positive")
            return True
    return False
def count_appointments(Location, URL):
    #URL="https://vaxfinder.mass.gov/locations/"
    #Location="210227094002Greenfield John Zon Center"
    file = open(Location+'.html', 'r')
    Lines = file.readlines()
    num_appointments=0
    if("https://www.maimmunizations.org/reg/" in URL):
        for i in range(len(Lines)):
            if ("appointments available" in Lines[i]):
                try:
                    num_appointments=num_appointments+int(Lines[i-1])
                except ValueError:
                    print("NOTHING")
                print("Found")
    elif("https://vaxfinder.mass.gov/locations/" in URL):
        for i in range(len(Lines)):
            if('<td class="align-right"><strong>' in Lines[i]):
                s_line=Lines[i]
                s_line=s_line.replace('<td class="align-right"><strong>','')
                s_line=s_line.replace('</strong></td>\n','')
                num_appointments=num_appointments+int(s_line)
                print("found")
    else:
        num_appointments =  -1
    file.close()
    return num_appointments

Vaccine_Site_File="/mnt/Dioscuri/Not Synced/Vaccine_Sites.csv"

df=pd.read_csv(Vaccine_Site_File)
df['Ignore_Time']=datetime.now()

while True:
    for index, row in df.iterrows():
        if(row['Ignore_Time']<datetime.now()):
            URL=row['URL']
            Trigger_Text=row['Trigger_Text']
            Location=row['Location']
            get_website(URL,Location)
            if(not catch_false_positive(Location)):
                if(check_status(Trigger_Text,Location,URL)):
                    df['Ignore_Time'][index]=datetime.now()+timedelta(hours=1)
            time.sleep(11+random.uniform(-10,10))
        