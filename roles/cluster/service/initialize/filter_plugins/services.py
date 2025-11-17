from ansible.errors import AnsibleFilterError




def list_services_only(host_templates):
    return sorted({service for group in host_templates.values() for service in group})


      
class FilterModule(object):
    def filters(self):
        return {
            'list_services_only': list_services_only
       }