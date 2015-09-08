
def regex_escape(string):
    from re import escape
    return escape(string)

class FilterModule(object):
    def filters(self):
        return {"regex_escape": regex_escape}

