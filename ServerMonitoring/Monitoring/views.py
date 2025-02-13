from django.shortcuts import render
from .models import *
import requests
from datetime import datetime, timedelta
import re

def CheckState(request):

    for server in Server.objects.all():
        url = f"http://{server.endPoint}"
        response = requests.get(url)
        date = response.json()
        print(date)
        pre = re.sub('[dhms]', '', date['uptime']).split(' ')
        con = timedelta(days=int(pre[0]), hours=int(pre[1]), minutes=int(pre[2]), seconds=int(pre[3]))
        print(con)
        ServerStat.objects.create(
            serverId = server,
            cpuLoad = date['cpu'],
            memLoad = date['ram'],
            diskLoad = date['disk'],
            upTime = con,
            сurrentTime = datetime.now()

            )