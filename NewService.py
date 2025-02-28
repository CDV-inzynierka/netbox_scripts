from extras.scripts import Script
from ipam.models import Prefix

class NewService(Script):
    class Meta:
        name = "List Available IPs from Fixed Prefix"
        description = "Lists the first available IP addresses from the fixed prefix 100.64.0.0/10 without reservation."

    def run(self, data, commit):
        prefix_obj=Prefix.objects.get(prefix="100.64.0.0/10")
        available_ip = prefix_obj.get_available_ips()
        
        self.log_success("Available IPs in master prefix:", str(available_ip))
        #if not available_ips:
        #    self.log_error("No available IP addresses in this prefix.")
        #    return
        #selected_ips = available_ips
        #for ip in selected_ips:
        #    self.log_success(str(ip))
