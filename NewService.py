from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix, Role, VLAN, VLANGroup,IPAddress
from tenancy.models import Tenant
from extras.models import CustomFieldChoiceSet
from netaddr import IPNetwork
from utilities.exceptions import AbortScript
from dcim.models import Device, Interface
import string
import random

class NewService(Script):
    class Meta:
        name = "Create a service for client"
        description = "Reserves a prefix for a new service from 100.64.0.0/10 range. Reserves a VLAN from pool dedicated for clients. Configures a port"
        scheduling_enabled = False

    PARENT_PREFIX="100.64.0.0/10"

    PrefixLength = ChoiceVar(
        description = "Select a mask for new service. Free addreses accounts in service needs of ISP (3 technical addresses)",
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

    Switch=ObjectVar(
        model=Device,
        description = "Pick a switch you would like add interface to. That field only helps you to filter interfaces attached to this switch",
        required = False,
        query_params={
            'role': 'switch-leaf'
        }
    )
    
    Interface=ObjectVar(
        model = Interface,
        label = "Interface",
        description = "Pick an interface to which this service should be bound. If desired port is not on the list, please check if it is not in use or lacks a Free Port tag",
        query_params = {
            'device_id': '$Switch',
            'tag': 'free-port'
        }
    )


    def run(self, data, commit):
        interface=data['Interface']

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
        #for descriptions usage
        formatted_prefix=str(ReservedPrefix).replace("/","_")

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
            prefix=ReservedPrefix,
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

        #creating virtual interfaces for config render
        RT0320_interface=Interface(
            device=Device.objects.get(name="RT0320"),
            name=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}_RT0320",
            type="virtual",
            parent=Interface.objects.get(tags=20),
            mode='access',
            untagged_vlan=new_vlan
        )
        RT0320_interface.save()
        RT0321_interface=Interface(
            device=Device.objects.get(name="RT0321"),
            name=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}_RT0321",
            type="virtual",
            parent=Interface.objects.get(tags=21),
            mode='access',
            untagged_vlan=new_vlan
        )
        RT0321_interface.save()
        self.log_success(f"Successfully created Interface objects: {RT0321_interface.name}, {RT0320_interface.name}")

        #creating IP addresses for L3 interfaces on vSRX routers
        vrrp_address=IPAddress(
            address=new_prefix.get_first_available_ip(),
            role="VRRP",
            tenant=data["Client"],
            description=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}"

        )
        vrrp_address.save()
        RT0320_address=IPAddress(
            address=new_prefix.get_first_available_ip(),
            tenant=data["Client"],
            description=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}",
        )
        RT0320_address.assigned_object=RT0320_interface
        RT0320_address.save()

        RT0321_address=IPAddress(
            address=new_prefix.get_first_available_ip(),
            tenant=data["Client"],
            description=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}",
        )
        RT0321_address.assigned_object=RT0321_interface
        RT0321_address.save()
        self.log_success(f"Successfully created IP Address objects: {RT0320_address.address}, {RT0321_address.address}, together with VRRP address: {vrrp_address.address}")

        #interface reservation

        #snapshot for data consistency and change logging
        if interface.pk and hasattr(Interface,'snapshot'):
            interface.snapshot()
        #modifying Netbox Interface object to assign it to vlan
        try:
            interface.mode="access"
            interface.untagged_vlan=new_vlan
            interface.description=f"{Name}_{data['Client'].slug}_{formatted_prefix}_{selected_bandwidth}"
            interface.full_clean()
            interface.save()
            self.log_success(f"Successfully bound a VLAN to interface: {interface.name}, {interface.device}")
        except Exception as e:
            raise AbortScript(f"An error occured during interface reservation: {str(e)}")
        
        #tagging outside of try block, most likely bug caused a problem with saving changes other than tag when tag was set in same save session
        interface.tags.set(['Service port'])
        interface.save()