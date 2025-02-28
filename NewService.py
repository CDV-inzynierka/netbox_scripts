from extras.scripts import Script
from ipam.models import Prefix

class NewService(Script):
    class Meta:
        name = "List Available IPs from Fixed Prefix"
        description = "Lists the first available IP addresses from the fixed prefix 100.64.0.0/10 without reservation."
        mask =(
            ('29', '/29'),
            ('28', '/28'),
            ('27', '/27'),
            ('26', '/26'),
            ('25', '/25'),
            ('24', '/24'),
            ('23', '/23'),
            ('22', '/22'),
            ('21', '/21'),
            ('20', '/20'),
            ('19', '/19'),
            ('18', '/18'),
            ('17', '/17'),
            ('16', '/16')
        )
        mask=ChoiceVar(choices=mask)


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
