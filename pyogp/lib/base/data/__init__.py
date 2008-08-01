from pkg_resources import resource_stream, resource_string

msg_tmpl = resource_stream(__name__, 'message_template.msg')
msg_details = resource_string(__name__, 'message.xml')
