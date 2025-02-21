from extras.scripts import Script
from ipam.models import Prefix

class NewService(Script):
    class Meta:
        name = "List Available IPs from Fixed Prefix"
        description = "Lists the first 30 available IP addresses from the fixed prefix 100.64.0.0/10 without reservation."

    def run(self, data, commit):
        fixed_prefix = "100.64.0.0/10"
        
        try:
            prefix_obj = Prefix.objects.get(prefix=fixed_prefix)
        except Prefix.DoesNotExist:
            self.log_error(f"Prefix not found: {fixed_prefix}")
            return
        available_ips_set = prefix_obj.get_available_ips()
        available_ips = list(available_ips_set)
        if not available_ips:
            self.log_error("No available IP addresses in this prefix.")
            return
        selected_ips = available_ips
        for ip in selected_ips:
            self.log_success(str(ip))
