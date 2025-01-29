from extras.scripts import *
from ipam.models import Prefix, IPAddress


class RunCommand(Script):
    class Meta:
        name = "Create a new Tenant"
        description ="todo"
    

    def run(self, data, commit):
        prefix="100.64.0.0/10"
        prefix_obj = Prefix.objects.get(prefix=prefix)
        available_ips = prefix_obj.get_available_ips()
        for x in 20:
            print(available_ips[x])
