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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
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
import urllib



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
    time.sleep(5)
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
    time.sleep(5)
    sel = Select(ff.find_element_by_id('selectstate'))
    sel.select_by_visible_text("Massachusetts")
    buttons=ff.find_elements_by_tag_name("button")
    for i in range (0,len(buttons)):
        if(buttons[i].text=="Get started"):
            buttons[i].click()
            break
def mercy_special(ff):
    ff.find_element_by_name("SiteName").click()
    time.sleep(5)
    ff.find_element_by_tag_name("button").click()
    for i in range(0,5):
        buttons=ff.find_elements_by_tag_name("button")
        for j in range (0,len(buttons)):
            if(buttons[j].text=="Next Day >"):
                buttons[j].click()
                break
        time.sleep(3)
        if('There are no open appointments on this day.' in ff.page_source):
            print("No Appointments")
        else:
            print("Appointment Found")
            break
def walgreens_special(ff):
    ff.find_element_by_link_text("Schedule new appointment").click()
    time.sleep(5)
    inputElement = ff.find_element_by_id("inputLocation")
    inputElement.clear()
    inputElement.send_keys('01038')
    inputElement.send_keys(Keys.ENTER)
    buttons=ff.find_elements_by_tag_name("button")
    for button in buttons:
        if(button.text=="Search"):
            button.click()
            break  
def color_special(ff):
    time.sleep(5)
    buttons=ff.find_elements_by_tag_name("button")
    for button in buttons:
        if(button.text=="Accept All Cookies"):
            button.click()
            break
    radio=ff.find_elements_by_name("receivedPreviousVaccinationOption")
    #I should be more clever in the future and actually have it check that the button says no
    radio[1].click()    
    inputElement = ff.find_element_by_id("birthday")
    inputElement.clear()
    inputElement.send_keys('01/01/1950')
    inputElement.send_keys(Keys.ENTER)
        
def check_file_valid(Location):
    if(path.exists(Location+".html")):
        if(os.stat(Location+".html").st_size == 0):
            print("File of Zero Size")
            return False
        else:
            return True
    else:
        print("File Missing")
        return False
    
def dump_html(browser,Location):
    with open(Location+'.html', 'w', encoding='utf-8') as f:
        f.write(browser.page_source)
        f.close()

def get_website(URL,Location,Check_Type):
    #URL="https://www.cvs.com/immunizations/covid-19-vaccine"
    #Location="Northampton"
    #Check_Type="CVS"
    if(Check_Type=="Color"):
        URL=URL+"vaccination-history"
    try:
        site_response = str(requests.get(URL))
    except:
        site_response = str(requests.get(URL,verify=False))
    if(site_response=="<Response [200]>" or site_response=="<Response [403]>"):
        ff = webdriver.Chrome(settings.ChromeDriverPath)
        maxattempts=30
        ff.get(URL)
        if(Check_Type=="CVS"):
            cvs_special(ff)
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("worcester", Location)):
                    time.sleep(2)
                    break
        elif(Check_Type=="Extra"):
            maxattempts=300
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("Which service(s) are you seeking?", Location)):
                    time.sleep(2)
                    break
        elif(Check_Type=="Mercy"):
            time.sleep(5)
            mercy_special(ff)
        elif(Check_Type=="Baystate"):
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("Registration Temporarily Unavailable", Location)):
                    break
                elif(check_for_text("Baystate Health Education Center", Location)):
                    time.sleep(2)
                    break
                elif(check_for_text("Baystate Health Education Center", Location)):
                    time.sleep(2)
                    break
        elif(Check_Type=="UMass"):
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("there are no time slots available at the moment to book first", Location)):
                    break
                elif(check_for_text("If you have not had any COVID-19 vaccinations click below", Location)):
                    time.sleep(2)
                    break
        elif(Check_Type=="maimmunization_reg"):
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("This clinic is closed. Please check other clinics.?", Location)):
                    break
                elif(check_for_text("Clinic does not have any appointment slots available.",Location)):
                    break
                elif(check_for_text("Please check back later to see if any appointments have become available",Location)):
                    break
                elif(check_for_text("Please select a time for your appointment.", Location)):
                    time.sleep(2)
                    break
        elif(Location=="Walgreens"):
            walgreens_special(ff)
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("Appointments unavailable", Location)):
                    break
                elif(check_for_text("Appointments available!", Location)):
                    time.sleep(2)
                    break
        elif(Check_Type=="Color"):
            color_special(ff)
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("There are currently no appointments available", Location)):
                    break
                elif(check_for_text("The page you were looking for can't be found.", Location)):
                    break
                elif(check_for_text("Select Location and Time", Location)):
                    time.sleep(2)
                    break
        elif(Location=="Vaccine Spotter"):
            for i in range(0,maxattempts):
                print(i)
                time.sleep(1)
                dump_html(ff,Location)
                if(check_for_text("No open appointments", Location)):
                    break
                elif(check_for_text("Appointments available", Location)):
                    time.sleep(2)
                    break
        else:
            if(Location=="Amherst Bangs Center"):
                for i in range(0,maxattempts):
                    print(i)
                    time.sleep(1)
                    dump_html(ff,Location)
                    if(check_for_text("Amherst Clinic Appointments", Location)):
                        time.sleep(2)
                        break
                    elif(check_for_text("https://www.google.com/url?q=https%3A%2F%2Fwww.maimmunizations.org%2F%2Freg", Location)):
                        time.sleep(2)
                        break
            elif(Location=="Northampton Clinic"):
                for i in range(0,maxattempts):
                    print(i)
                    time.sleep(1)
                    dump_html(ff,Location)
                    if(check_for_text("Both sites are open to all Massachusetts residents who are eligible to receive the vaccine. ", Location)):
                        time.sleep(2)
                        break
                    elif(check_for_text("https://www.maimmunizations.org//reg/", Location)):
                        time.sleep(2)
                        break
            else:
                time.sleep(30)
        dump_html(ff,Location)
        ff.quit()
    else:
        print("FAILED: " + URL)
    if(check_file_valid(Location)):
        print("Download complete")
    else:
        try:
            os.remove(Location+".html")
            print("File Not Valid")
        except:
            print("File Doesn't Exist")
def check_for_text(Trigger_Text, Location):
    with open(Location+'.html', encoding='utf-8') as f:
        if Trigger_Text in f.read():
            return True
        else:
            return False
def count_baystate():
    URL="https://mobileprod.api.baystatehealth.org/workwell/schedules/campaigns?camId=mafirstresp210121&activeOnly=1&includeVac=1&includeSeat=1%27"
    count=0
    site=urllib.request.urlopen(URL)
    lines = site.readlines()
    s_line=str(lines[0])
    while(not s_line.find('dose1Available":')==-1):
        position=s_line.find('dose1Available":')+16
        s_line=s_line[position:]
        position=s_line.find(',')
        s_line2=s_line[0:position]
        count=int(s_line2)+count
        s_line=s_line[position:]
    return count

def check_status(Trigger_Text, Location, URL):  
    #Trigger_Text="Anything"
    #Location="NewTest"
    #URL="https://vaxfinder.mass.gov/locations/"
    print("Checking " + Location)
    if(check_for_text(Trigger_Text,Location)):
        print(gettime() + " No Appointments")
        return False
    else:
        print(gettime() + " Vaccine may be available")
        num_appointments=count_appointments(Location, URL)
        if(num_appointments >= 0 and num_appointments<10):
            if(Location=="Baystate Health"):
                broadcast("Vaccine may be available at "+ Location +"\n"+ URL +"\n" + gettime())
            else:
                print(gettime() + " No Appointments")
        elif(num_appointments==-1):
            if(Location=="Walgreens"):
                broadcast("Vaccine may be available at a Walgreens in the Pioneer Valley, check with Walgreens for specific locations"+"\n"+ URL +"\n"+ gettime())
            else:
                broadcast("Vaccine may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        else:
            broadcast(str(num_appointments) + " vaccine appointments may be available at "+ Location +"\n"+ URL +"\n" + gettime())
        archivehtml(Location, "found vaccine")
        return True
    
def con_google_redirect(URL):
    #URL='https://www.google.com/url?q=https%3A%2F%2Fwww.maimmunizations.org%2F%2Freg%2F1560324950&amp;sa=D&amp;sntz=1&amp;usg=AFQjCNFeJUbyawISY9F9Vwuqn6EENo0zCQ'
    if('https://www.google.com/url?q=' in URL):
        URL=URL.replace('https://www.google.com/url?q=','')
        position=URL.find('&amp')
        URL=URL[0:position]
        URL=URL.replace('%3A',':')
        URL=URL.replace('%2F','/')
    return URL

def get_subsite(s_line,Trigger_Text,URL_List):
    #URL_List=[]
    position=s_line.find(Trigger_Text)
    s_line=s_line[position:]
    position=s_line.find('"')
    s_line[0:position]
    URL=con_google_redirect(s_line[0:position])
    s_line=s_line[position:]
    if(position>=0):
        URL_List.append(URL)
        get_subsite(s_line,Trigger_Text,URL_List)
    else:
        pass
    return URL_List


    
def check_subpage(Trigger_Text, Location, URL):  
    #Trigger_Text="https://www.google.com/url?q=https%3A%2F%2Fwww.maimmunizations.org"
    #Location="NewTest"
    #URL="https://www.google.com/url?q=https%3A%2F%2Fwww.maimmunizations.org"
    URL_List=[]
    print("Checking " + Location)
    num_appointments = 0
    if(check_for_text(Trigger_Text,Location)):
        print(gettime() + " Trigger Text Found")
        file = open(Location+'.html', 'r', encoding='utf-8')
        Lines = file.readlines()
        for i in range(len(Lines)):
            get_subsite(Lines[i],Trigger_Text,URL_List)
        for i in range(0,len(URL_List)):
            pass
            get_website(URL_List[i],Location+str(i),'maimmunization_reg')
        for i in range(0,len(URL_List)):
            num_appointments+=count_appointments(Location+str(i), URL_List[i])
        print(num_appointments)
        if(num_appointments>=10):
            print(gettime() + " Vaccine may be available")
            broadcast(str(num_appointments) + " vaccine appointments may be available at "+ Location +"\n"+ URL +"\n" + gettime())
            archivehtml(Location, "found vaccine")
            for i in range(0,len(URL_List)):
                archivehtml(Location+str(i), "found vaccine")
            return True
        else:
            print(gettime() + " No Appointments")
            return False
    else:
        print(gettime() + " No Appointments")
        return False
        
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
    if("maimmunizations.org/" in URL):
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
        if(Location=="Baystate Health"):
            try:
                num_appointments = count_baystate()
            except:
                num_appointments = - 1
        else:
            num_appointments =  -1
    file.close()
    return num_appointments
def get_vaccine_type(Location):
    #Location="MA_Immunization5"
    vaxtype="unknown"
    file = open(Location+'.html', 'r', encoding='utf-8')
    Lines = file.readlines()
    for i in range(len(Lines)):
        s_line=Lines[i]
        if('data-pfizer-clinic="true"'  in Lines[i]):
            vaxtype="Pfizer"
            pass
        if('data-moderna-clinic="true"'   in Lines[i]):
            vaxtype="Moderna"
            pass
        if('data-janssen-clinic="true"'  in Lines[i]):
            vaxtype="Johnson & Johnson"
            pass        
    return vaxtype
        
def check_vaccine_spotter(Site):
    Location="Vaccine Spotter"
    #Site="Shaw's - 180 A Cambridge Street, Burlington, MA, 01803"
    file = open(Location+'.html', 'r', encoding='utf-8')
    Found=False
    Lines = file.readlines()
    s_line=''
    URL=''
    step=0
    num_appointments=-1
    for i in range(len(Lines)):
        if (step==0 and Site in Lines[i]):
            s_line=Lines[i]
            Found=True
            step=step+1
        elif(step==1 and 'return false;">View ' in Lines[i]):
            s_line=Lines[i]
            position=s_line.find('return false;">View ')+20
            s_line=s_line[position:]
            position=s_line.find(' other appointment times')
            s_line=s_line[0:position]
            num_appointments=int(s_line)+5
            step=step+1
        elif(step>=1 and '<!----> <a href="' in Lines[i]):
            s_line=Lines[i]
            position=s_line.find('href="')+6
            s_line=s_line[position:]
            position=s_line.find('"')
            URL=s_line[0:position]
        elif(step>=1 and 'Last checked' in Lines[i]):
            break
    file.close()
    if(Found):
        if(num_appointments==-1):
            broadcast("Vaccine may be available at "+ Site + '\n' + URL +"\n" + gettime())
        elif(num_appointments>0):
            broadcast(str(num_appointments) + " appointments may be available at "+ Site + '\n' + URL +"\n" + gettime())
        archivehtml(Location, "found vaccine")
        return True
    else:
        print(gettime() + " No Appointments")
        return False
def check_cvs(Site,Location,URL):
    #URL="https://www.cvs.com/immunizations/covid-19-vaccine"
    #Location="CVS"
    #Site=Trigger_Text
    file = open(Location+'.html', 'r', encoding='utf-8')
    Lines = file.readlines()
    s_line=''
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
    if(SiteNum>0):
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
    else:
        print("Failed To Load Sites CVS")
        return False
def read_ma_immunization(SitesFound):
    #SitesFound = []
    #SitesIgnore = []
    URL="https://clinics.maimmunizations.org/clinic/search?q%5Bservices_name_in%5D%5B%5D=Vaccination&location=01038&search_radius=25+miles&q%5Bvenue_search_name_or_venue_name_i_cont%5D=&clinic_date_eq%5Byear%5D=&clinic_date_eq%5Bmonth%5D=&clinic_date_eq%5Bday%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results"
    Location="MA_Immunization"
    Check_Type="Extra"
    get_website(URL,Location,Check_Type)
    if(path.exists(Location+".html")):
        file = open(Location+'.html', 'r', encoding='utf-8')
        Lines = file.readlines()
        columns = ['Site','Location','Num','Vaccine', 'URL','Ignore_Time']
        df2 = pd.DataFrame( columns=columns)
        Link=""
        for i in range(len(Lines)):
            if ('<p class="text-xl font-black">' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace('      ','')
                Loc=s_line.replace('\n','')
                #print(Location)
            if(' MA, 0' in Lines[i]):
                s_line=Lines[i]
                position=s_line.find(',')+2
                s_line=s_line[position:]
                position=s_line.find(',')
                City=s_line=s_line[0:position]
            if('Vaccinations offered:' in Lines[i]):
                s_line=Lines[i+2]
                position=len(s_line) - len(s_line.lstrip())
                s_line=s_line[position:]
                s_line=s_line.replace('\n','')
                VaccineType=s_line
            if('<strong>Available Appointments:</strong>' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace(':</strong>','')
                #s_line=s_line.replace('</p>','')
                n_appointment=int(s_line.replace(' ',''))
                #print(n_appointment)
            if('<p class="my-3 flex">' in Lines[i]):
                s_line=Lines[i+1]
                s_line=s_line.replace('<a class="button-primary px-4" href="','')
                s_line=s_line.replace('">','')
                s_line=s_line.replace(' ','')
                Link='https://clinics.maimmunizations.org'+s_line
                #print(s_line)
            if('<div class="map-image mt-4 md:mt-0 md:flex-shrink-0">' in Lines[i]):
                df2 = df2.append({'Site' : Loc,'Location' : City, 'Num' : n_appointment,'Vaccine' : VaccineType, 'URL' : Link, 'Ignore_Time' : datetime.now()},  
                    ignore_index = True) 
                Link=""
        for index, row in df2.iterrows():
            print(gettime() + " Checking " + row['Site'])
            if(not row['URL']==''):
                AlreadyFound=False
                for i in range(0,(int(len(SitesFound)/2)),1):
                    if(SitesFound[i*2]==row['Site']):
                        AlreadyFound=True
                if(not AlreadyFound):
                    get_website(row['URL'],Location+str(index),'maimmunization_reg')
                    num_appointments=count_appointments(Location+str(index), row['URL'])
                    vaxtype=row['Vaccine']
                    if(vaxtype==''):
                        vaxtype=get_vaccine_type(Location+str(index))
                    if(num_appointments>=10):
                        print(row['Site'])
                        SitesFound.append(row['Site'])
                        SitesFound.append(datetime.now()+timedelta(hours=3))
                        print(gettime() + " Vaccine may be available")
                        broadcast(str(num_appointments) + " appointments may be available at "+ row['Site'] +" in " +row['Location'] + "\n" + vaxtype + "\n" + row['URL']+"\n" + gettime())
                        archivehtml(Location, "found vaccine")
                        archivehtml(Location+str(index), "found vaccine")
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
            SitesFound.pop(position)
            SitesFound.pop(position-1)
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
                try:
                    get_website(URL,Location,Check_Type)
                except:
                    print("Problem Loading")
            else:
                print("Already Downloaded")
            if(path.exists(Location+".html")):
                if(not catch_false_positive(Location)):
                    if(Check_Type=="Mercy"):
                        try:
                            if(check_status(Trigger_Text,Location,URL)):
                                df['Ignore_Time'][index]=datetime.now()+timedelta(hours=3)
                        except:
                            print("Problem in Mercy Check")
                    elif(Check_Type=="CVS"):
                        if(check_cvs(Trigger_Text,Location,URL)):
                            df['Ignore_Time'][index]=datetime.now()+timedelta(hours=8)
                    elif(Check_Type=='subpage'):
                        try:
                            if(check_subpage(Trigger_Text, Location, URL)):
                                df['Ignore_Time'][index]=datetime.now()+timedelta(hours=3)
                        except:
                            print("Problem in subpage checker")
                    elif(Check_Type=='VaccineSpotter'):
                        try:
                            if(check_vaccine_spotter(Trigger_Text)):
                                df['Ignore_Time'][index]=datetime.now()+timedelta(hours=6)
                        except:
                            print("Problem in vaccine spotter checker")
                    else:
                        if(check_status(Trigger_Text,Location,URL)):
                            if(Location=="Walgreens"):
                                df['Ignore_Time'][index]=datetime.now()+timedelta(hours=6)
                            else:
                                df['Ignore_Time'][index]=datetime.now()+timedelta(hours=3)
            else:
                print(Location + " Failed to Download Skipping")
            #time.sleep(random.uniform(0,1))
    try:
        MA_SitesFound=read_ma_immunization(MA_SitesFound)
    except:
        print("Something went wrong you should probably fix it")
    MA_SitesFound=checksiteignore(MA_SitesFound)
    clean_up()
        