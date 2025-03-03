from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix
from tenancy.models import Tenant
from ipaddress import ip_network

class NewService(Script):
    class Meta:
        name = "List Available IPs from Fixed Prefix"
        description = "Lists the first available IP addresses from the fixed prefix 100.64.0.0/10 without reservation."
        scheduling_enabled = False

    PARENT_PREFIX="100.64.0.0/10"

    PrefixLength = ChoiceVar(
        description = "Select a mask for new service. Free addreses accounts in service needs of ISP (3 technical addresses).",
        label = "Mask",
        choices=(
        ('29', '/29 - 3 addresses'),
        ('28', '/28 - 11 addresses'),
        ('27', '/27 - 27 addresses'),
        ('26', '/26 - 59 addresses'),
        ('25', '/25 - 123 addresses'),
        ('24', '/24 - 251 addresses'),
        ('23', '/23 - 507 addresses'),
        ('22', '/22 - 1019 addresses'),
        ('21', '/21 - 2043 addreses'),
        ('20', '/20 - 4091 addresses'),
        ('19', '/19 - 8187 addreses'),
        ('18', '/18 - 16379 addresses'),
        ('17', '/17 - 32763 addresses'),
        ('16', '/16 - 65531 addresses')
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
        #finding all avialable prefixes in master 100.64.0.0/10
        FreePrefix=[]
        PrefixObj = Prefix.objects.get(prefix=self.PARENT_PREFIX)
        PrefixLengthFilter = int(data['PrefixLength'])
        AvailablePrefixes = PrefixObj.get_available_prefixes()

        #conversion to string
        FreePrefix = [str(ip) for ip in AvailablePrefixes.iter_cidrs()]
        #checking if desired prefix lenght from ChoiceVar fits in any of free prefixes
        for f in FreePrefix:
            f=ip_network(f)
            if PrefixLengthFilter >= f.prefixlen:
                ReservedPrefix=f
                break
        #raising exception if no free prefixes found
        if ReservedPrefix==None:
            raise AbortScript(f"No free prefixes in master prefix") # type: ignore
        
        new_prefix=Prefix(
            prefix=ReservedPrefix,
            status="reserved",
            tenant=self.Client
            
        )
        new_prefix.save()

        
        self.log_success(f"First available prefix with given mask: {ReservedPrefix}")

        
