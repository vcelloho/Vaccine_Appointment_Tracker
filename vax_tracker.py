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
import os
import os.path
from os import path
import glob
from pathlib import Path



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
    to_number = settings.PhoneNumber+carriers[settings.Carrier]
    auth = (settings.EmailAddress, settings.EmailPassword)

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP(settings.EmailSTMPAddress, settings.EmailSTMPPort )
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail( auth[0], to_number, message)
def broadcast(message):
    if(settings.DevMode):
        print(message)
    else:
        if(settings.Tweet):
            tweet(message)
        if(settings.SMS):
            message=message.replace('https://','')
            message=message.replace('www.','')
            send(message)
def gettime():
    now = datetime.now()
    return(now.strftime("%D %H:%M:%S"))
def getdate():
    now = datetime.now()
    return(now.strftime("%y%m%d%H%M%S"))

def archivehtml(Location,arch_type):
    if(arch_type=="false positive"):
        copyfile(Location+'.html', 'False Positive Archive/'+getdate() +Location+'.html')
    if(arch_type=="found vaccine"):
        copyfile(Location+'.html', 'Vaccine Site Archive/'+getdate() +Location+'.html')
def cvs_special(ff):
    ff.find_element_by_link_text("Massachusetts").click()
def check_file_valid(Location):
    if(os.stat(Location+".html").st_size == 0):
        return False
    else:
        return True
def get_website(URL,Location,Check_Type):
    #URL="https://www.cvs.com/immunizations/covid-19-vaccine"
    #Location="CVS"
    if(str(requests.get(URL))=="<Response [200]>" or str(requests.get(URL))=="<Response [403]>"):
        ff = webdriver.Chrome(settings.ChromeDriverPath)
        #ff = webdriver.Chrome('G:/@@@/Programs/chromedriver.exe')
        ff.get(URL)
        if(Check_Type=="CVS"):
            cvs_special(ff)
        elif(Check_Type=="Extra"):
            time.sleep(30)
        time.sleep(30)
        with open(Location+'.html', 'w', encoding='utf-8') as f:
            f.write(ff.page_source)
        ff.quit()
        f.close()
    else:
        print("FAILED: " + URL)
    if(check_file_valid(Location)):
        print("Download complete")
    else:
        os.remove(Location+".html")
        print("File Not Valid")
def check_for_text(Trigger_Text, Location):
    with open(Location+'.html', encoding='utf-8') as f:
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
        if(num_appointments<10):
            print(gettime() + " No Appointments")
        elif(num_appointments==-1):
            broadcast("Vaccine may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        else:
            broadcast(str(num_appointments) + " vaccine appointments may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        archivehtml(Location, "found vaccine")
        return True
        
def catch_false_positive(Location):
    fp_list=pd.read_csv(settings.FalsePositiveCSV)
    for index,row in fp_list.iterrows():
        if(check_for_text(row['False_Positives'],Location)):
            print(gettime() + " False Positive " + Location)
            archivehtml(Location, "false positive")
            return True
    return False
def count_appointments(Location, URL):
    #URL="https://vaxfinder.mass.gov/locations/"
    #Location="Palmer CVS"
    file = open(Location+'.html', 'r', encoding='utf-8')
    Lines = file.readlines()
    num_appointments=0
    num_time_slots = 0
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
                num_time_slots += 1
                print("found")
        if(num_time_slots == 0 and num_appointments == 0):
            num_appointments = -1
    else:
        num_appointments =  -1
    file.close()
    return num_appointments
def check_cvs(Site,Location,URL):
    #URL="https://www.cvs.com/immunizations/covid-19-vaccine"
    #Location="CVS"
    #Site=Trigger_Text
    file = open(Location+'.html', 'r', encoding='utf-8')
    Lines = file.readlines()
    for i in range(len(Lines)):
        if ('<tbody><tr><td><span class="city">' in Lines[i]):
            s_line=Lines[i]
    s_line=s_line.replace('\t\t\t<tbody><tr><td><span class="city">','')
    s_line=s_line.replace('</span></td></tr></tbody>\n','')
    s_line=s_line.replace(', MA</span></td><td><span class="status">','|')
    s_line=s_line.replace('</span></td></tr><tr><td><span class="city">','|')
    s_line=s_line.title()
    site_list = s_line.split("|")
    SiteNum=int(len(site_list)/2)
    for i in range(SiteNum,0,-1):
        if(not site_list[(i-1)*2]==Site):
            site_list.pop((i-1)*2)
            site_list.pop((i-1)*2)
    if(site_list[1]=="Available"):
        print(gettime() + " Vaccine may be available")
        broadcast("Vaccine may be available at the "+ Site +" CVS\n"+ URL +"\n" + gettime())
        archivehtml(Location, "found vaccine")
        return True
        pass
    elif(site_list[1]=="Fully Booked"):
        print(gettime() + " No Appointments")
        return False
    else:
        print("There may be a problem")
        return False
def read_ma_immunization(SitesFound):
    #SitesFound = []
    #SitesIgnore = []
    URL="https://www.maimmunizations.org/clinic/search?location=01002&search_radius=25+miles&q%5Bvenue_search_name_or_venue_name_i_cont%5D=&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results"
    Location="MA_Immunization"
    Check_Type="Extra"
    get_website(URL,Location,Check_Type)
    if(path.exists(Location+".html")):
        file = open(Location+'.html', 'r', encoding='utf-8')
        Lines = file.readlines()
        columns = ['Site','Num', 'URL','Ignore_Time']
        df2 = pd.DataFrame( columns=columns)
        Link=""
        for i in range(len(Lines)):
            if ('<p class="text-xl font-black">' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace('      ','')
                Loc=s_line.replace('\n','')
                #print(Location)
            if('<p><strong>Available Appointments' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace(':</strong>','')
                s_line=s_line.replace('</p>','')
                n_appointment=int(s_line.replace(' ',''))
                #print(n_appointment)
            if('<p class="my-3 flex">' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace('<a class="button-primary px-4" href="','')
                s_line=s_line.replace('">','')
                s_line=s_line.replace(' ','')
                Link='https://www.maimmunizations.org'+s_line
                #print(s_line)
            if('<div class="map-image mt-4 md:mt-0 md:flex-shrink-0">' in Lines[i]):
                df2 = df2.append({'Site' : Loc, 'Num' : n_appointment, 'URL' : Link, 'Ignore_Time' : datetime.now()},  
                    ignore_index = True) 
                Link=""
        for index, row in df2.iterrows():
            print(gettime() + " Checking " + row['Site'])
            if(row['Num']>= 10 and not row['URL']==''):
                AlreadyFound=False
                for i in range(0,(int(len(SitesFound)/2)),1):
                    if(SitesFound[i*2]==row['Site']):
                        AlreadyFound=True
                if(not AlreadyFound):
                    print(row['Site'])
                    SitesFound.append(row['Site'])
                    SitesFound.append(datetime.now()+timedelta(hours=1))
                    print(gettime() + " Vaccine may be available")
                    broadcast(str(int(row['Num'])) + " appointments may be available at "+ row['Site'] + "\n" +row['URL']+"\n" + gettime())
                    archivehtml(Location, "found vaccine")
                    time.sleep(11+random.uniform(-10,10))
                else:
                    print("Already Found Ignoring")
        file.close()
    else:
        print(Location + " Failed to Download Skipping")
    return SitesFound
def checksiteignore(SitesFound):
    listlength=len(SitesFound)
    for i in range(0,(int(listlength/2)),1):
        position=listlength-1-2*i
        if(SitesFound[position]<datetime.now()):
            SitesFound.pop()
            SitesFound.pop()
    return SitesFound
        
def clean_up():
    fileList = glob.glob('*.html', recursive=True)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")

df=pd.read_csv(settings.Vaccine_Site_File)
df['Ignore_Time']=datetime.now()
Path("Vaccine Site Archive").mkdir(parents=True, exist_ok=True)
Path("False Positive Archive").mkdir(parents=True, exist_ok=True)
MA_SitesFound=[]
while True:
    for index, row in df.iterrows():
        if(row['Ignore_Time']<datetime.now()):
            URL=row['URL']
            Trigger_Text=row['Trigger_Text']
            Location=row['Location']
            Check_Type=row['Check_Type']
            if(not path.exists(Location+".html")):
               get_website(URL,Location,Check_Type)
            else:
                print("Already Downloaded")
            if(path.exists(Location+".html")):
                if(not catch_false_positive(Location)):
                    if(Check_Type=="normal"):
                        if(check_status(Trigger_Text,Location,URL)):
                            df['Ignore_Time'][index]=datetime.now()+timedelta(hours=1)
                    elif(Check_Type=="CVS"):
                        if(check_cvs(Trigger_Text,Location,URL)):
                            df['Ignore_Time'][index]=datetime.now()+timedelta(hours=1)
            else:
                print(Location + " Failed to Download Skipping")
            time.sleep(6+random.uniform(-5,5))
    try:
        MA_SitesFound=read_ma_immunization(MA_SitesFound)
    except:
        print("Something went wrong you should probably fix it")
    MA_SitesFound=checksiteignore(MA_SitesFound)
    clean_up()
        