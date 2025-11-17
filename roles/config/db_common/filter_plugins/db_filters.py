# filter_plugins/db_filters.py



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
            'append_database_port': append_database_port,
            'format_database_type': format_database_type
        }
