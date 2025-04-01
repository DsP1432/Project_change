from urllib.request import urlopen
from pushbullet import Pushbullet
import ssl
import time
import os
from datetime import datetime
import sys
import difflib

#site_data
#[0]name
#[1]url
#[2]type_of_search
#[3]source_code
#[4]time_of_change
#[5]error_code
#[6]time_of_error
#[7]error
#[8]last_scan_time
#[9]found_status

if "android" in os.path.basename(__file__):
    clear_or_cls="clear"
elif "windows" in os.path.basename(__file__):
    clear_or_cls="cls"
else:
    clear_or_cls=None

def clear():
    global clear_or_cls
    if clear_or_cls=="clear":
        os.system("clear")
    elif clear_or_cls=="cls":
        os.system("cls")

def add_log(text):
    with open("log.txt","a+") as f:
        f.writelines(["\n",datetime.now().strftime("%d-%m-%Y %I:%M:%S %p : "),text,"\n"])

with open("main.txt","r") as f:
    lines=f.readlines()
    pushbullet_id=lines[0].strip()[14:]
    del lines[0]
    repeat_notification=int(lines[0].strip()[20:])
    del lines[0]
    notification_delay=int(lines[0].strip()[19:])
    del lines[0]
    scan_delay=int(lines[0].strip()[11:])
    del lines[0]
    site_data=[]
    temp=[]
    while len(lines)!=0:
        temp.append(lines[1].strip()[6:])
        temp.append(lines[2].strip()[5:])
        temp.append(lines[3].strip()[1:])
        site_data.append(temp)
        del lines[:4]
        temp=[]

print("Scanning first time.\nGetting website data. 0/"+str(len(site_data))+" done.")

pb=Pushbullet(pushbullet_id)

for i in range(len(site_data)):
    site_data[i].append("")

for i in range(len(site_data)):
    try:
        context = ssl._create_unverified_context()
        response = urlopen(site_data[i][1],context=context)
        page_source = response.read().decode()
        if site_data[i][2]=="all":
            site_data[i][3]=page_source
        elif site_data[i][2].startswith("rem="):
            temp=site_data[i][2]
            site_data[i][3]=page_source[:int(temp[4:temp.find(":")])]+page_source[int(temp[temp.find(":")+1:]):]
        elif site_data[i][2].startswith("only="):
            temp=site_data[i][2]
            site_data[i][3]=page_source[int(temp[5:temp.find(":")]):int(temp[temp.find(":")+1:])]
    except Exception as e:
        print("Error occured in getting data with "+site_data[i][0]+" : "+str(e))
        sys.exit()
    else:
        clear()
        init_time=datetime.now().strftime("%H:%M:%S")
        print("Scanning first time.\nGetting website data. "+str(i+1)+"/"+str(len(site_data))+str(" done."))
        
for i in range(len(site_data)):
    site_data[i].append([])
    site_data[i].append(0)
    site_data[i].extend(["" for j in range(4)])
    site_data[i].append(0)

notification_send_status=[[] for i in range(len(site_data))]

counter=0
n=int(notification_delay/scan_delay)
first_counter=1

time.sleep(1)
clear()

print("First scanned at "+init_time+"\n")
for i in range(len(site_data)):
    print(str(i+1)+". "+site_data[i][0]+". Checking...")

while True:
    response_data=[0 for i in range(len(site_data))]
    for i in range(len(site_data)):
        try:
            site_data[i][8]=datetime.now().strftime("%H:%M:%S")
            response = urlopen(site_data[i][1],context=context)
            page_source = response.read().decode()
            if site_data[i][2].startswith("rem="):
                temp=site_data[i][2]
                page_source=page_source[:int(temp[4:temp.find(":")])]+page_source[int(temp[temp.find(":")+1:]):]
            elif site_data[i][2].startswith("only="):
                temp=site_data[i][2]
                page_source=page_source[int(temp[5:temp.find(":")]):int(temp[temp.find(":")+1:])]
            if site_data[i][2].startswith("find="):
                keyword=site_data[i][2][5:]
                if keyword in page_source and site_data[i][9]!=1:
                    site_data[i][9]=1
                    site_data[i][4].append(datetime.now().strftime("%H:%M:%S"))
                    notification_send_status[i].append(1)
                    change=difflib.ndiff(site_data[i][3].split(),page_source.split())
                    site_data[i][3]=page_source
                    temp_removed=""
                    temp_added=""
                    for j in change:
                        if j.startswith("-"):
                            temp_removed+=j[2:]+" | "
                        elif j.startswith("+"):
                            temp_added+=j[2:]+" | "
                    add_log("\n\tRemoved from "+site_data[i][0]+": "+temp_removed+"\n\tAdded to "+site_data[i][0]+": "+temp_added)
            elif page_source!=site_data[i][3]:
                site_data[i][4].append(datetime.now().strftime("%H:%M:%S"))
                notification_send_status[i].append(1)
                change=difflib.ndiff(site_data[i][3].split(),page_source.split())
                site_data[i][3]=page_source
                temp_removed=""
                temp_added=""
                for j in change:
                    if j.startswith("-"):
                        temp_removed+=j[2:]+" | "
                    elif j.startswith("+"):
                        temp_added+=j[2:]+" | "
                add_log("\n\tRemoved from "+site_data[i][0]+": "+temp_removed+"\n\tAdded to "+site_data[i][0]+": "+temp_added)
        except Exception as e:
            site_data[i][5]=1
            site_data[i][6]=datetime.now().strftime("%H:%M:%S")
            site_data[i][7]=e
        else:
            site_data[i][5]=0
        if first_counter==1:
            clear()
            print("First scanned at "+init_time+"\n")
            for j in range(len(site_data)):
                if site_data[j][5]==0:
                    if site_data[j][8]!="":
                        if len(site_data[j][4])!=0:
                            print(str(j+1)+". Changes detected on "+site_data[j][0]+". Last updated at "+site_data[j][8]+".")
                        else:
                            print(str(j+1)+". No change detected on "+site_data[j][0]+". Last updated at "+site_data[j][8]+".")
                    else:
                        print(str(j+1)+". "+site_data[j][0]+". Checking...")
                else:
                    print(str(j+1)+". Error on "+site_data[j][0]+" at "+site_data[j][6]+" : "+str(site_data[i][7]))
    clear()
    first_counter=0
    counter+=1
    if counter==n:
        for i in range(len(site_data)):
            if len(site_data[i][4])!=0:
                for j in range(len(site_data[i][4])):
                    if notification_send_status[i][j]==1:
                        try:
                            pb.push_note("Change detected","Change detected on "+site_data[i][0]+" at "+site_data[i][4][j]+".")
                        except Exception as e:
                            if repeat_notification==0:
                                add_log("Could not send notification for "+site_data[i][0]+" due to "+str(e))
                        else:
                            if repeat_notification==0:
                                notification_send_status[i][j]=0
        counter=0
    print("First scanned at "+init_time+"\n")
    for i in range(len(site_data)):
        if site_data[i][5]==0:
            if len(site_data[i][4])!=0:
                print(str(i+1)+". Changes detected on "+site_data[i][0]+". Last updated at "+site_data[i][8]+".")
            else:
                print(str(i+1)+". No change detected on "+site_data[i][0]+". Last updated at "+site_data[i][8]+".")
        else:
            print(str(i+1)+". Error on "+site_data[i][0]+" at "+site_data[i][6]+" : "+str(site_data[i][7])+".")
        if len(site_data[i][4])!=0:
            for j in range(len(site_data[i][4])):
                if repeat_notification==0:
                    if notification_send_status[i][j]==0:
                        status="sent"
                    else:
                        status="unsent"
                print("\t"+str(j+1)+". ("+status+") Change detected at "+site_data[i][4][j]+".")
    time.sleep(scan_delay)
        
