
from django.shortcuts import render

from .models import *
import requests
from datetime import datetime, timedelta, timezone
import re
from django_q.tasks import Schedule

def CheckState():
        server_obj_list = []
        for server in Server.objects.all():

            url = f"http://{server.endPoint}"

            try:
                response = requests.get(url)
            except requests.ConnectionError:
                continue
            else:
                data = response.json()
                cleanDate = re.sub('[dhms]', '', data['uptime']).split(' ')
                delta = timedelta(days=int(cleanDate[0]), hours=int(cleanDate[1]), minutes=int(cleanDate[2]), seconds=int(cleanDate[3]))
                res = ServerStat(
                    serverId = server, 
                    cpuLoad = data['cpu'], 
                    memLoad = data['ram'], 
                    diskLoad = data['disk'], 
                    upTime = delta, 
                    currentTime = datetime.now())
                
                server_obj_list.append(res)
            
            
        return server_obj_list
        
        
def RunCheck():
    
    l = CheckState()
    saveToBase(l)
    
    dectectwarning()

def saveToBase(servers):
    ServerStat.objects.bulk_create(servers)

def dectectwarning():
    sheludetime = Schedule.objects.get().minutes
    
    for server in Server.objects.all():

        laststamp = ServerStat.objects.filter(serverId=server).order_by('-currentTime')[:1].first()
       
        if (laststamp.currentTime < datetime.now(timezone.utc) - server.maxtimeout):
             shutdown = datetime.now(timezone.utc)-laststamp.currentTime
             print(type(shutdown))
             WarningStat.objects.create(
                  serverId=laststamp.serverId, 
                  cpuLoad=0, 
                  memLoad=0, 
                  diskLoad=0, 
                  upTime=timedelta(days=0, hours=0, minutes=0), 
                  currentTime=datetime.now(), 
                  servershutdown=timedelta(days=shutdown.days, seconds=shutdown.seconds))

        else: 
            memdelta = laststamp.currentTime - timedelta(minutes=server.memtimelimit)
            cpudelta = laststamp.currentTime - timedelta(minutes=server.cputimelimit)
            diskdelta = laststamp.currentTime - timedelta(minutes=server.disktimelimit)

            memtimeseries = ServerStat.objects.filter(serverId=server).filter(currentTime__range=(memdelta, laststamp.currentTime))
            cputimeseries = ServerStat.objects.filter(serverId=server).filter(currentTime__range=(cpudelta, laststamp.currentTime))
            disktimeseries = ServerStat.objects.filter(serverId=server).filter(currentTime__range=(diskdelta, laststamp.currentTime))
        
                
            if any(
                [highornot(server.cpulimit, 'cpuLoad', cputimeseries),
                highornot(server.memlimit, 'memLoad', memtimeseries),
                highornot(server.disklimit, 'diskLoad', disktimeseries),]
            ):
                
                    WarningStat.objects.create(
                         serverId=laststamp.serverId,
                         cpuLoad=laststamp.cpuLoad,
                         memLoad=laststamp.memLoad, 
                         diskLoad=laststamp.diskLoad, 
                         upTime=laststamp.upTime, 
                         currentTime=laststamp.currentTime)
                #print(highornot(server.memlimit, 'memLoad', t[:2])) 
     
def highornot(limit, part, dataseries):
    return all([getattr(stamp, part) > limit for stamp in dataseries])     
        