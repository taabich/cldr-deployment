from ansible.errors import AnsibleFilterError

def generate_host_templates(host_templates, hostvars, kerberos_enabled=False):
    # Count how many hosts per template
    template_counts = {}
    for host, vars in hostvars.items():
        tpl = vars.get('host_template')
        if tpl:
            template_counts[tpl] = template_counts.get(tpl, 0) + 1

    result = []
    for tpl_name, services in host_templates.items():
        role_config_groups = []
        for service, roles in services.items():
            for role in roles:
                role_config_groups.append(f"{service.lower()}-{role.upper()}-BASE")
        if service.lower() == 'hue' and kerberos_enabled:
            role_config_groups.append(f"{service.lower()}-KT_RENEWER-BASE")
        
        if  template_counts.get(tpl_name, 0) >0:
            result.append({
                "refName": f"HostTemplate-{tpl_name}",
                "cardinality": template_counts.get(tpl_name, 1),
                "roleConfigGroupsRefNames": role_config_groups
            })

    return result


def count_service_role(host_templates, hostvars, service_name, role_name):
    # Count how many hosts per template
    template_counts = {}
    for host, vars in hostvars.items():
        tpl = vars.get('host_template')
        if tpl:
            template_counts[tpl] = template_counts.get(tpl, 0) + 1

    count = 0
    for tpl_name, services in host_templates.items():
        
        for service, roles in services.items():
            if service.lower() != service_name.lower():
                continue
            for role in roles:
                if role.lower() == role_name.lower():
                    count = count + template_counts.get(tpl_name, 0)
                     
    return count



def list_host_byservice(host_templates, hostvars, service_name, role_name):
    matching_templates = set()

    # Step 1: find templates containing the desired service/role
    for tpl_name, services in host_templates.items():
        for service, roles in services.items():
            if service.lower() == service_name.lower() and any(
                role.lower() == role_name.lower() for role in roles
            ):
                matching_templates.add(tpl_name)

    # Step 2: collect hosts mapped to those templates
    matching_hosts = [
        host
        for host, vars in hostvars.items()
        if vars.get("host_template") in matching_templates
    ]
    print( matching_hosts )
    return matching_hosts


def list_services_only(host_templates):
    return sorted({service for group in host_templates.values() for service in group})

def format_database_type( database_type):
        if database_type == "mariadb":
            return "mysql"
        return database_type.lower()
def append_database_port( database_host, database_port=None):
    if ":" not in database_host and database_port:
        return database_host + ":" + database_port
    return database_host
      
class FilterModule(object):
    def filters(self):
        return {
            'generate_host_templates': generate_host_templates,
            'list_services_only': list_services_only,
            'format_database_type': format_database_type,
            'append_database_port': append_database_port,
            'list_host_byservice': list_host_byservice,
            'count_service_role':count_service_role
        }