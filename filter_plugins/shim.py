
def regex_escape(string):
    """returns the given string after escaping any regex characters"""
    from re import escape
    return escape(string)

class FilterModule(object):
    def filters(self):
        return {"regex_escape": regex_escape}

