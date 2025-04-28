from extras.scripts import Script,ObjectVar
from ipam.models import Prefix, VLAN
from tenancy.models import Tenant
from utilities.exceptions import AbortScript
from dcim.models import Interface, Device

class DeleteService(Script):
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
        unset_interface=Interface.objects.get(untagged_vlan=deleted_vlan, tags=2)
        RT0320_object=Device.objects.get(name="RT0320")
        RT0321_object=Device.objects.get(name="RT0321")

        unset_rt0320_interface=Interface.objects.get(untagged_vlan=deleted_vlan, device=RT0320_object)
        unset_rt0321_interface=Interface.objects.get(untagged_vlan=deleted_vlan, device=RT0321_object)
        try:
            try:
                deleted_prefix.delete()
                self.log_success(f"Succesfully deleted a prefix: {deleted_prefix.prefix}")
            except Exception as e:
                raise AbortScript(f"An error occured during deleting a prefix: {str(e)}") 
            
            try:
                unset_rt0320_interface.delete()
                unset_rt0321_interface.delete()
                self.log_success(f"Succesfully deleted Interfaces: {unset_rt0320_interface.name}, {unset_rt0320_interface.name}")
            except Exception as e:
                raise AbortScript(f"An error occured during deleting interfaces: {str(e)}") 

            try:
                deleted_vlan.delete()
                self.log_success(f"Succesfully deleted a VLAN: {deleted_vlan.name} with ID: {str(deleted_vlan.vid)}")
            except Exception as e:
                raise AbortScript(f"An error occured during deleting a vlan: {str(e)}") 
            

            try:

                if unset_interface.pk and hasattr(Interface,'snapshot'):
                    unset_interface.snapshot()

                unset_interface.untagged_vlan=None
                unset_interface.mode=""
                unset_interface.description=""
                unset_interface.full_clean()
                unset_interface.save()
                self.log_success(f"Interface {unset_interface.name}, {unset_interface.device} successfully unbound")
            except Exception as e:
                raise AbortScript(f"An error occured during reconfiguring an interface: {str(e)}")
        except Exception as e:
            raise AbortScript(f"Deleting service unsuccesful")
        
        #tagging outside of try block, most likely bug caused a problem with saving changes other than tag when tag was set in same save session
        unset_interface.tags.set(['Free port'])
        unset_interface.save()


