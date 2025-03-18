from extras.scripts import Script,ChoiceVar,ObjectVar
from ipam.models import Prefix, Role, VLAN, VLANGroup
from tenancy.models import Tenant
from utilities.exceptions import AbortScript
from netaddr import IPNetwork
import string
import random

class NewService(Script):
    class Meta:
        name = "Delete a service"
        description = "Deletes a service."
        scheduling_enabled = False

    Client=ObjectVar(
        model=Tenant,
        description = "Pick a client you would like to modify",
    )
    
    Prefix=ObjectVar(
        model = Prefix,
        label = "Service",
        description = "Pick a service to delete",
        query_params = {
            'tenant_id': '$Client',
            'role': 'client'
        }
    )



    def run(self, data, commit):
        
        TempPrefix=data['Prefix']
        deleted_prefix=TempPrefix
        deleted_vlan=VLAN.objects.get(name=TempPrefix.description)
        try:
            deleted_prefix.delete()
            self.log_success(f"Succesfully deleted a prefix: {deleted_prefix.prefix}")
        except Exception as e:
            raise AbortScript(f"An error occured during deleting a prefix: {str(e)}") # type: ignore

        try:
            deleted_vlan.delete()
            self.log_success(f"Succesfully deleted a VLAN: {deleted_vlan.name} with ID: {deleted_vlan.id}")
        except Exception as e:
            raise AbortScript(f"An error occured during deleting a vlan: {str(e)}") # type: ignore

