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
    votes_250 = urllib2.urlopen('https://verein.ing-diba.de/club/presentation/search/page/50/category//clubname//location//size//order/rank/direction/ASC')
    html_250 = votes_250.read()

    abschnitt=re.findall("<li>Stimmen: \d\.?\d*</li>\s*<li>Rang: 250</li>", html_250)
    stimmen_250=re.findall('Stimmen: \d\.?\d*',abschnitt[kategorie])[0][-5:]
    stimmen_250=int(stimmen_250.replace(".",""))

    votes_target = urllib2.urlopen(url)
    html_target= votes_target.read()
    abschnitt2=re.findall('Stimmen.*<span class="headline">Mitglieder<br />26 - 75</span>',html_target, re.DOTALL)[0]
    stimmen_target=re.findall('<h2 class="xl">.*</h2>',abschnitt2)[0][-10:-5]
    stimmen_target=int(stimmen_target.replace(".",""))
    print "Stimmen Platz 250: %s" %stimmen_250
    print "Stimmen Eigener Verein: %s" %stimmen_target
    print "Differenz: %s" %(stimmen_target-stimmen_250)
    return stimmen_250, stimmen_target


stimmen_250, stimmen_target=check_votes()
text="Stimmen Platz 250: {}\nStimmen Eigener Verein: {}\nDifferenz: {}\n".format(stimmen_250,stimmen_target,stimmen_target-stimmen_250)
subject="ING-Vote-Monitoring gestartet..."
send_mail(from_adress,from_password,to_adress,text,subject,True)


start=dt.datetime.today()+dt.timedelta(seconds=3)
alerts=0

while True:
    now=dt.datetime.today()
    if now>=start:
        alertsold=alerts
        print dt.datetime.today()
        try:
            stimmen_250, stimmen_target=check_votes()
            if stimmen_target<stimmen_250-20:
                print "Too few votes, gogogo!"
                text="Stimmen Platz 250: {}\nStimmen Eigener Verein: {}\nDifferenz: {}\n".format(stimmen_250,stimmen_target,stimmen_target-stimmen_250)
                subject="Alert: too few Votes at ING!"
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
            check_intervall+=dt.timedelta(hours=6)
    time.sleep(1)

