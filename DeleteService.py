from extras.scripts import Script,ObjectVar
from ipam.models import Prefix, VLAN
from tenancy.models import Tenant
from utilities.exceptions import AbortScript
from dcim.models import Interface

class NewService(Script):
    class Meta:
        name = "Delete a service"
        description = "Deletes a service."
        scheduling_enabled = False
    Client=ObjectVar(
        model=Tenant,
        description = "Pick a client you would like to modify. That field only helps you to filter services attached to this client.",
        required = False
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
        
        deleted_prefix=data['Prefix']
        deleted_vlan=VLAN.objects.get(name=deleted_prefix.description)
        unset_interface=Interface.objects.get(untagged_vlan=deleted_vlan)
        try:
            try:
                deleted_prefix.delete()
                self.log_success(f"Succesfully deleted a prefix: {deleted_prefix.prefix}")
            except Exception as e:
                raise AbortScript(f"An error occured during deleting a prefix: {str(e)}") 

            try:
                deleted_vlan.delete()
                self.log_success(f"Succesfully deleted a VLAN: {deleted_vlan.name} with ID: {str(deleted_vlan.vid)}")
            except Exception as e:
                raise AbortScript(f"An error occured during deleting a vlan: {str(e)}") 

            try:

                if unset_interface.pk and hasattr(Interface,'snapshot'):
                    unset_interface.snapshot()

                unset_interface.untagged_vlan=None
                unset_interface.mode=None
                unset_interface.description=None
                unset_interface.full_clean()
                unset_interface.save()
                self.log_debug(f"debug")
                self.log_success(f"Interface {unset_interface.name} successfully unbound")
            except Exception as e:
                raise AbortScript(f"An error occured during reconfiguring an interface: {str(e)}")
        except Exception as e:
            raise AbortScript(f"Deleting service unsuccesful")
        
        unset_interface.tags.set(['Free port'])
        unset_interface.save()


