from django.db import models


class Server(models.Model):
    endPoint = models.CharField(max_length=5000)
    name = models.CharField(max_length=200)



class ServerStat(models.Model):
    serverId = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpuLoad = models.FloatField() 
    memLoad = models.FloatField()
    diskLoad = models.FloatField()
    upTime = models.DurationField()
    сurrentTime = models.DateTimeField()

