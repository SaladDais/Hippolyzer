from pkg_resources import resource_stream

msg_tmpl = resource_stream(__name__, 'message_template.msg')
