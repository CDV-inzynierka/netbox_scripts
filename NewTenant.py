from extras.scripts import Script
from ipam.models import Prefix

class ListAvailableIPs(Script):
    class Meta:
        name = "Create a new Tenant"


    def run(self, data, commit):
        prefix_obj = Prefix.objects.get(prefix='100.64.0.0/10')        
        available_ips = prefix_obj.get_available_ips()
        if not available_ips:
            self.log_error("No free IPs in that prefix.")
            return
        num_to_display = min(data['count'], 30)
        selected_ips = available_ips[:num_to_display]

        self.log_info(f"First {num_to_display} free IP addresses in {data['prefix']} prefix:")
        for ip in selected_ips:
            self.log_success(ip)
