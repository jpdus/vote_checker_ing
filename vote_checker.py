__author__ = 'jph'

import urllib2
import re
import datetime as dt
from sendmail import send_mail
import time

###############################################
#Settings:

kategorie=2 #Kategore 1-4 von klein nach gross
url="https://verein.ing-diba.de/kinder-und-jugend/example/example" #vereins page auf der ING seite
check_intervall=dt.timedelta(hours=2) #intervall zwischen den abfragen
from_adress="example@gmail.com"
from_password="123456"
to_adress=["example2@gmail.com"]

###############################################


kategorie-=1

def check_votes():
    votes_200 = urllib2.urlopen('https://verein.ing-diba.de/club/presentation/search/page/40/category//clubname//location//size//order/rank/direction/ASC')
    html_200 = votes_200.read()

    abschnitt=re.findall("<li>Stimmen: \d\.?\d*</li>\s*<li>Rang: 200</li>", html_200)
    stimmen_200=re.findall('Stimmen: \d\.?\d*',abschnitt[kategorie])[0][-5:]
    stimmen_200=int(stimmen_200.replace(":",""))

    votes_target = urllib2.urlopen(url)
    html_target= votes_target.read()
    stimmen_target=re.findall('Stimmen: \d\.?\d*',html_target)[0][-5:]
    stimmen_target=int(stimmen_target.replace(":",""))
    #print "Stimmen Platz 200: %s" %stimmen_200
    #print "Stimmen Eigener Verein: %s" %stimmen_target
    #print "Differenz: %s" %(stimmen_target-stimmen_200)
    with open('log.txt','a') as logfile:
        logfile.write('{},{},{},{}\n'.format(dt.datetime.today(),stimmen_200,stimmen_target,stimmen_target-stimmen_200))
    print logfile.closed
    return stimmen_200, stimmen_target


stimmen_200, stimmen_target=check_votes()
text="Stimmen Platz 200: {}\nStimmen Eigener Verein: {}\nDifferenz: {}\n".format(stimmen_200,stimmen_target,stimmen_target-stimmen_200)
subject="ING-Vote-Monitoring gestartet..."
#send_mail(from_adress,from_password,to_adress,text,subject,True)


start=dt.datetime.today()+dt.timedelta(seconds=3)
nextalert=start+dt.timedelta(hours=24)
alerts=0

while True:
    now=dt.datetime.today()
    if now>=start:
        alertsold=alerts
        print dt.datetime.today()
        try:
            stimmen_200, stimmen_target=check_votes()
            if stimmen_target<stimmen_200-20:
                print "Too few votes, gogogo!"
                text="Stimmen Platz 200: {}\nStimmen Eigener Verein: {}\nDifferenz: {}\n".format(stimmen_200,stimmen_target,stimmen_target-stimmen_200)
                print text
                subject="Alert: too few Votes at ING!"
                if now>=nextalert:
                    send_mail(from_adress,from_password,to_adress,text,subject,True)
                    alerts+=1
            else:
                print "Vote difference big enough - waiting..."
        except urllib2.URLError:
            print "Website not available"
            subject="Alert: ING Website not available"
            text="\n"
            send_mail(from_adress,from_password,to_adress,text,subject,True)
            alerts+=1
        start=now+check_intervall
        if alerts!=alertsold:
            nextalert+=dt.timedelta(hours=24)
    time.sleep(1)

