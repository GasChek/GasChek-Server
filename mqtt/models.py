from django.db import models


class Mqtt_Servers(models.Model):
    server = models.CharField(max_length=255)
    server_url = models.CharField(max_length=255)
    port = models.IntegerField()
    keepalive = models.IntegerField()
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    qos = models.IntegerField(default=1)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.server} - {self.user}"
