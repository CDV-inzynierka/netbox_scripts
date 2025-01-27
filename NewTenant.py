from extras.scripts import *
from ipam.models import Prefix, IPAddress


class RunCommand(Script):
    class Meta:
        name = "todo"
        description ="todo"
    prefix="100.64.0.0/10"

    def run(self):
        prefix_obj = Prefix.objects.get(prefix=data['prefix'])
        available_ips = prefix_obj.get_available_ips()
        for x in 20:
            print(available_ips[x])
