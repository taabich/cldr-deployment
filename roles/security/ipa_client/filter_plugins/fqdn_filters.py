from ansible.plugins.filter import core

def extract_domain(fqdn):
    """Extract domain by removing the first part of the FQDN"""
    return ".".join(fqdn.split(".")[1:]) if "." in fqdn else fqdn

class FilterModule(object):
    """ Custom Jinja2 filters for FQDN processing """
    def filters(self):
        return {
            'extract_domain': extract_domain
        }