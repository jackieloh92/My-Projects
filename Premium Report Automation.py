#!/usr/bin/env python
# coding: utf-8

#importing all the necessary modules in order to get this project up and running

import pandas as pd
import numpy as np
import datetime
import openpyxl
import os
import schedule
import time
import calendar
import email, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from openpyxl.cell import Cell
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, Color, Fill

#defining global variables at the top of the code for convenient viewing

today = datetime.date.today()

# defining the month map for management to have a clearer view of the month name instead of seeing month digits

month_name = {
1:'January',
2:'February',
3:'March',
4:'April',
5:'May',
6:'June',
7:'July',
8:'August',
9:'September',
10:'October',
11:'November',
12:'December'}


#Defining the function that will read the excel file from its source, and do the necessary data cleaning & analysis in pandas dataframe

def analyse_data():
    source = pd.ExcelFile('PREMIUM_DATA.xlsx')
    policy = pd.read_excel(source, sheet_name="POLICY")
    premium = pd.read_excel(source, sheet_name="PREMIUM")
    
    #merging both worksheets together into 1 full table for easier data processing

    df = pd.merge(policy,premium)
    
    #check to see if there are any missing values. We need accurate data, and should leave all NaN fields out

    df.isnull()

    # if there are any missing values for any of the data records, I would flag it out to IT, and remove it from our analysis first so that the data is accurate.

    df.dropna()
    
    # Creating a dataframe that only shows positive values for GWP. 
    # My best guess at the cryptic column names given by IT is that GWP = Gross Written Premium


    GWPbooked = df.loc[df.GWP>0]
    GWPcancelled = df.loc[df.GWP<0]
    
    #inserting new columns to clearly show the year that the GWP was booked/cancelled

    GWPbooked['Transaction Year'] = GWPbooked['D_tran'].dt.year
    GWPbooked['Transaction Month'] = GWPbooked['D_tran'].dt.month
    GWPcancelled['Transaction Year'] = GWPcancelled['D_tran'].dt.year
    GWPcancelled['Transaction Month'] = GWPcancelled['D_tran'].dt.month
    
    #Using the GroupBy function to break down the GWP by its line of business, month and year

    GWPbookedgrouped = GWPbooked['GWP'].groupby([GWPbooked['lob'],GWPbooked['Transaction Year'],GWPbooked['Transaction Month']])

    #Converting the GWPbookedgrouped results to a dataframe, so we can see it clearly and proceed to export to Excel format for management's viewing purposes.

    GWPbookedgrouped = pd.DataFrame(GWPbookedgrouped.sum())

    #Resetting the dataframe index so that all columns will be recognised, and remove any blank indexes

    GWPbookedgrouped = GWPbookedgrouped.reset_index()

    #Mapping the monthly digits (1-12) to the appropriate month names (January - December) 

    GWPbookedgrouped['Transaction Month'] = GWPbookedgrouped['Transaction Month'].map(month_name)

    #Duplicating the same instructions for all Gross Written Premium Cancelled

    GWPcancelledgrouped = GWPcancelled['GWP'].groupby([GWPcancelled['lob'],GWPcancelled['Transaction Year'],GWPcancelled['Transaction Month']])
    GWPcancelledgrouped = pd.DataFrame(GWPcancelledgrouped.sum())
    GWPcancelledgrouped.sort_values(by=['lob','Transaction Year','Transaction Month'])
    GWPcancelledgrouped = GWPcancelledgrouped.reset_index()
    GWPcancelledgrouped['Transaction Month'] = GWPcancelledgrouped['Transaction Month'].map(month_name)
    
    #We will write the results of our grouped dataframe to a new excel file, for management's perusal

    managementfile = pd.ExcelWriter('Monthly Premium Report.xlsx', engine='xlsxwriter')
    GWPbookedgrouped.to_excel(managementfile, sheet_name='Gross Written Premium Booked')
    GWPcancelledgrouped.to_excel(managementfile, sheet_name='Gross Written Premium Cancelled')
    managementfile.save()


#Next step, defining the edit excel function to make the excel spreadsheet easier to read. This is where the design and aesthetics should come in
#I admit I did not spend alot of time here to make the spreadsheet look very beautiful, but I hope this code shows some of the potential of openpyxl library
    
def edit_excel():
    managementfile = pd.ExcelWriter('Monthly Premium Report.xlsx', engine='xlsxwriter')
    newFile = (managementfile)
    wb = openpyxl.load_workbook(filename = newFile)        
    worksheet = wb.active
    
    #Setting a thin border for the columns and indexes

    thin_border = Border(left=Side(style='thin'), 
                     right=Side(style='thin'), 
                     top=Side(style='thin'), 
                     bottom=Side(style='thin'))

    
    #Changing the column names from its original cryptic version to something that would make sense

    wsbooked = wb['Gross Written Premium Booked']
    wsbooked['A1'] = 'Line of Business'
    wsbooked['B1'] = 'Transaction Year'
    wsbooked['C1'] = 'Transaction Month'
    wsbooked['D1'] = 'Gross Written Premium Booked'
    
    #Resizing the column width for all valid rows/columns so the text does not get hidden or squashed

    dims = {}
    for row in wsbooked.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))    
    for col, value in dims.items():
        wsbooked.column_dimensions[col].width = value+5
    wsbooked.border = thin_border
  
    #Duplicating the same instructions for the GWP cancelled worksheet tab

    wscancelled = wb['Gross Written Premium Cancelled']
    wscancelled['A1'] = 'Line of Business'
    wscancelled['B1'] = 'Transaction Year'
    wscancelled['C1'] = 'Transaction Month'
    wscancelled['D1'] = 'Gross Written Premium Booked'
    dims = {}
    
    for row in wscancelled.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))    
    for col, value in dims.items():
        wscancelled.column_dimensions[col].width = value+5
        
    wscancelled.border = thin_border
    
    
    #Applying some font colours, bold, and alignment to make it more neat

    red_font = Font(color='00FF0000', italic=True)
    
    for cell in wsbooked["1:1"]:
        cell.font = Font(b=True, color="FF0000")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for cell in wscancelled["1:1"]:
        cell.font = Font(b=True, color="FF0000")
        cell.alignment = Alignment(horizontal="center", vertical="center")
     
    #Of course, we save the file. This step acts as an auto-update of editing the excel sheet everytime the scheduler runs

    wb.save(newFile)
    
    
#Finally, this code will run on a periodic basis, to send out the Monthly report file out to management
#I will remove my Google Password, so this code will not run until someone fills in their username/password
    
def send_mail():
   
    fromaddr = "jackieloh92@gmail.com"
    toaddr = "jackieloh92@gmail.com"
   
    # instance of MIMEMultipart 
    msg = MIMEMultipart() 
  
    # storing the senders email address   
    msg['From'] = fromaddr 
  
    # storing the receivers email address  
    msg['To'] = toaddr 
  
    #added the today string so that management can see that this report is as of 'today' 
    msg['Subject'] = "Monthly AXA Report " + str(today)
  
    # string to store the body of the mail. 
    body = "Dear Management team, \n This is the monthly report as of " + str(today)
  
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
  
    # open the file to be sent  
    filename = "Monthly AXA Report.xlsx"
    attachment = open("Monthly Premium Report.xlsx", "rb") 
  
    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
  
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
  
    # encode into base64 
    encoders.encode_base64(p) 
   
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
  
    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 
  
    # creates SMTP session. For testing purposes, I have used a Gmail address and port
    s = smtplib.SMTP('smtp.gmail.com', 587) 
  
    # start TLS for security 
    s.starttls() 
  
    # Authentication. This is where I would fill in the server username and password. I have removed my password here, so the code will not run until there's a proper user/pw

    s.login('jackieloh92@gmail.com', 'insert_password_here') 
  
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
  
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
  
    # terminating the session 
    s.quit() 
    
def job():

    #defining the applicable variables to calculate the last working day of each month

    now = datetime.datetime.now()
    cy=now.year #current year
    cm=now.month #current month
 
    last_day=calendar.monthrange(cy,cm)[1] #last day of currrent month
 
    #the date and name of the last day of month

    date_ld=datetime.date(cy,cm,last_day)
    date_ld_name=calendar.day_name[date_ld.weekday()]
 
    #the date of last Workday of month

    if date_ld_name=="Saturday":
        date_ld=date_ld - datetime.timedelta(days=1)
    elif date_ld_name=="Sunday":
        date_ld=date_ld - datetime.timedelta(days=2)
 
    #if today is workday-1 then send the reminder via e-mail

    if today_date==date_ld:
        analyse_data()
        #The data takes around 10 seconds to process. I set a sleep timer for 30 seconds just in case the file gets larger
        time.sleep(30)
        edit_excel()
        time.sleep(30)
        send_mail()
    else:
        pass

if __name__ == '__main__':

#This code will check on a daily basis if the function job has detected that it's already the last day of the month. If it is truly the last day, the code will execute all the sub-functions
    
schedule.every(1).day.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)






