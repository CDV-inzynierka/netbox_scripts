from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix, Role, VLAN, VLANGroup
from tenancy.models import Tenant
from extras.models import CustomFieldChoiceSet
from netaddr import IPNetwork
from utilities.exceptions import AbortScript
import string
import random

class NewService(Script):
    class Meta:
        name = "Create a service for client"
        description = "Reserves a prefix for a new service from 100.64.0.0/10 range. Reserves a VLAN from pool dedicated for clients"
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
    CircuitBandwidth=ChoiceVar(
       description="Select a bandwidth for new service",
       label = "Circuit bandwidth",
       choices=CustomFieldChoiceSet.objects.get(name="Bandwidth").extra_choices,
       default='50'
    )
    Client = ObjectVar(
        model = Tenant
    )


    def run(self, data, commit):
        #finding all avialable prefixes in master 100.64.0.0/10
        FreePrefix=[]
        AvailablePrefixes = Prefix.objects.get(prefix=self.PARENT_PREFIX).get_available_prefixes()
        PrefixLengthFilter = int(data['PrefixLength'])

        #conversion to string
        FreeMasterPrefix = [str(ip) for ip in AvailablePrefixes.iter_cidrs()]
        #checking if desired prefix lenght from ChoiceVar fits in any of free prefixes
        for f in FreeMasterPrefix:
            f=IPNetwork(f)
            if PrefixLengthFilter >= f.prefixlen:
                ReservedPrefix=f
                break
        #raising exception if no free prefixes found
        if FreePrefix==None:
            raise AbortScript(f"No free prefixes in master prefix") 
        
        #constructing prefix to reservation
        ReservedPrefix.prefixlen=PrefixLengthFilter
        characters=string.ascii_uppercase+string.digits
        Name="".join(random.choices(characters, k=5))
        #creating Netbox VLAN object
        new_vlan=VLAN(
            vid=VLANGroup.objects.get(name="Vlany Kliencie").get_next_available_vid(),
            name=Name,
            role=Role.objects.get(name="Client"),
            group=VLANGroup.objects.get(name="Vlany Kliencie"),
            tenant=data["Client"]
        )

        new_vlan.save()
        self.log_success(f"Succesfully created a VLAN: {new_vlan.name} with ID: {new_vlan.vid}")

        selected_bandwidth=data['CircuitBandwidth']
        #creating Netbox Prefix object
        new_prefix=Prefix(
            prefix=ReservedPrefix, # type: ignore
            status="reserved",
            tenant=data["Client"],
            role=Role.objects.get(name="Client"),
            vlan=new_vlan,
            description=Name,
            custom_field_data={
                'bandwidth': selected_bandwidth
            }
        )
        new_prefix.save()
        
        self.log_success(f"Succesfully reserved a prefix: {ReservedPrefix}")
