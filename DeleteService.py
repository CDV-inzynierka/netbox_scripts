from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix, Role, VLAN, VLANGroup
from tenancy.models import Tenant
from extras.models import CustomFieldChoiceSet
from netaddr import IPNetwork
import string
import random

class NewService(Script):
    class Meta:
        name = "Delete a service"
        description = "Deletes a service."
        scheduling_enabled = False

    Client = ObjectVar(
        model = Tenant
    )
    CircuitBandwidth=ChoiceVar(
       description="Select a bandwidth for new service",
       label = "Circuit bandwidth",
       choices=CustomFieldChoiceSet.objects.get(name="Bandwidth").extra_choices,
       default='50'
    )



    def run(self, data, commit):

        self.log_success(f"Succesfully deleted a VLAN: {deleted_vlan.name} with ID: {deleted_vlan.id}")

        
        self.log_success(f"Succesfully deleted a prefix: {deleted_prefix.prefix}")
