from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix
from tenancy.models import Tenant

class NewService(Script):
    class Meta:
        name = "List Available IPs from Fixed Prefix"
        description = "Lists the first available IP addresses from the fixed prefix 100.64.0.0/10 without reservation."
        scheduling_enabled = False

    PARENT_PREFIX="100.64.0.0/10"

    PrefixLength = ChoiceVar(
        description = "Select a mask for new service",
        label = "Mask",
        choices=(
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
        ),
        default='29'
    )
    CircuitSpeed = ChoiceVar(
        description = "Select a policer for new service",
        label = "Speed",
        choices=(
        ('50', '50 Mbps'),
        ('100', '100 Mbps'),
        ('200', '200 Mbps'),
        ('300', '300 Mbps'),
        ('500', '500 Mbps'),
        ('1000', '1 Gbps')
        ),
        default='50'
    )
    Client = ObjectVar(
        model = Tenant

    )


    def run(self, data, commit):
        PrefixObj=Prefix.objects.get(prefix=self.PARENT_PREFIX)
        PrefixLengthFilter=int(data['PrefixLength'])
        AvailableIP = PrefixObj.get_available_prefixes().filter(prefix_length=PrefixLengthFilter).first()

        self.log_success("First available prefix with given mask:", str(AvailableIP))
        
        #if not available_ips:
        #    self.log_error("No available IP addresses in this prefix.")
        #    return
        #selected_ips = available_ips
        #for ip in selected_ips:
        #    self.log_success(str(ip))
