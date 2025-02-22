from datetime import datetime, timedelta
from django.db import models


class Server(models.Model):
    endPoint = models.CharField(max_length=5000)
    name = models.CharField(max_length=200)
    cpulimit = models.FloatField()
    memlimit = models.FloatField()
    disklimit = models.FloatField()
    cputimelimit = models.IntegerField(default=15)
    memtimelimit = models.IntegerField(default=15)
    disktimelimit = models.IntegerField(default=15)
    maxtimeout = models.DurationField(timedelta(minutes=60))

    def __str__(self):
        return self.name

class Stat(models.Model):
    serverId = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpuLoad = models.FloatField() 
    memLoad = models.FloatField()
    diskLoad = models.FloatField()
    upTime = models.DurationField()
    currentTime = models.DateTimeField()
    

    def __str__(self):
        return str(self.serverId)
    class Meta:
        abstract=True

class ServerStat(Stat):
    pass

class WarningStat(Stat):
    servershutdown = models.DurationField(default=timedelta(minutes=00))
    