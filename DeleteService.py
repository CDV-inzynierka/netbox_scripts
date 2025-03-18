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





    def run(self, data, commit):

        self.log_success(f"Succesfully deleted a VLAN: {deleted_vlan.name} with ID: {deleted_vlan.id}")

        
        self.log_success(f"Succesfully deleted a prefix: {deleted_prefix.prefix}")
