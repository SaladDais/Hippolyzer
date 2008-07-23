from zope.configuration.xmlconfig import xmlconfig

def init():
    from pkg_resources import resource_stream
    fp = resource_stream(__name__, 'configure.zcml')
    xmlconfig(fp)