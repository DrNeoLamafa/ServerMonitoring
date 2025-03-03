from .models import *
import requests
from datetime import datetime, timedelta, timezone
import re


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
                    serverid = server, 
                    cpuload = data['cpu'], 
                    memload = data['ram'], 
                    diskload = data['disk'], 
                    uptime = delta, 
                    currenttime = datetime.now())
                
                server_obj_list.append(res)
            
            
        return server_obj_list
        
        
def RunCheck():
    
    server_obj_list = CheckState()
    saveToBase(server_obj_list)
    
    dectectwarning()

def saveToBase(servers):
    ServerStat.objects.bulk_create(servers)

def dectectwarning():
   
    for server in Server.objects.all():

        laststamp = ServerStat.objects.filter(serverid=server).order_by('-currenttime')[:1].first()
        if (laststamp is None):
            
            continue
       # если сервер в таймауте больше лимита
        
        if (laststamp.currenttime < datetime.now() - server.maxtimeout):
            
            shutdown = datetime.now() - laststamp.currenttime
            WarningStat.objects.create(
                serverid=laststamp.serverid, 
                cpuload=0, 
                memload=0, 
                diskload=0, 
                uptime=timedelta(days=0, hours=0, minutes=0), 
                currenttime=datetime.now(), 
                serverdowntime=timedelta(days=shutdown.days, seconds=shutdown.seconds)) 
        
        else: 

            cputimelimit = timedelta(minutes=server.cputimelimit)
            memtimelimit = timedelta(minutes=server.memtimelimit)
            disktimelimit = timedelta(minutes=server.disktimelimit)
            #если аптайм больше любого из параметров, то можно проверять 
           
            if any([laststamp.uptime > limit for limit in [cputimelimit, memtimelimit, disktimelimit]]):     
                
                #окна по временным лимитам для каждого параметра
                memdelta = laststamp.currenttime - memtimelimit
                cpudelta = laststamp.currenttime - cputimelimit
                diskdelta = laststamp.currenttime - disktimelimit

                # наборы данных в диапазоне по времени
                
                memtimeseries = ServerStat.objects.filter(serverid=server).filter(currenttime__range=(memdelta, laststamp.currenttime))
                cputimeseries = ServerStat.objects.filter(serverid=server).filter(currenttime__range=(cpudelta, laststamp.currenttime))
                disktimeseries = ServerStat.objects.filter(serverid=server).filter(currenttime__range=(diskdelta, laststamp.currenttime))
            
                # если любой из параметров вышел за лимит - warning
                if any(
                    [highornot(server.cpulimit, 'cpuload', cputimeseries),
                    highornot(server.memlimit, 'memload', memtimeseries),
                    highornot(server.disklimit, 'diskload', disktimeseries),]
                ):
                    
                        WarningStat.objects.create(
                            serverid=laststamp.serverid,
                            cpuload=laststamp.cpuload,
                            memload=laststamp.memload, 
                            diskload=laststamp.diskload, 
                            uptime=laststamp.uptime, 
                            currenttime=laststamp.currenttime)
                    
     
def highornot(limit, part, dataseries):
    return all([getattr(stamp, part) > limit for stamp in dataseries])     
        