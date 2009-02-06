#!/usr/bin/python

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..', '..')))

from optparse import OptionParser
import binascii
from pyogp.lib.base.message.udpdeserializer import UDPPacketDeserializer
from logging import getLogger, StreamHandler, Formatter, CRITICAL, ERROR, WARNING, INFO, DEBUG

logger = getLogger('parse_packet')
log = logger.log


def main():

    (options) = parse_options()

    if options.verbose: enable_logging()

    data = options.data
    datatype = options.datatype

    msg_buff = gen_message_buffer(data, datatype)
    
    deserializer = UDPPacketDeserializer(msg_buff)
    packet = deserializer.deserialize()

    #print packet.__dict__
    display_packet(packet)

def parse_options():

    parser = OptionParser()

    parser.add_option("-t", "--type", dest="datatype", default="hex", help="datatype to parse, default = hex")
    parser.add_option("-d", "--data", dest="data", help="data to parse")
    parser.add_option("-v", "--verbose", dest="verbose", default=True, action="store_false")

    (options, args) = parser.parse_args()

    return options

def gen_message_buffer(data, datatype):

    if datatype == 'hex':
        return message_buff_from_hex(data)

    return

def message_buff_from_hex(data):

    return binascii.unhexlify(''.join(data.split()))

def display_packet(packet):

    delim = "    "
    print 'Packet Name:%s%s' % (delim, packet.name)

    for k in packet.__dict__:
        if k == 'name': pass
        if k == 'message_data':
            print k
            for ablock in packet.message_data.blocks:
                print "%sBlock Name:%s%s" % (delim, delim, ablock)
       
                for somevars in packet.message_data.blocks[ablock]:
                    for avar in somevars.var_list:
                        zvar = somevars.get_variable(avar)
                        print "%s%s%s:%s%s" % (delim, delim, zvar.name, delim, zvar.get_data_as_string())
        #print '%s:\t%s' % (k, packet.__dict__[k])
        #print '%s:\t%s (%s)' (k, packet.__dict__[k], type(packet.__dict__[k]))

    '''
    for k,v in packet.__dict__:
        if type(v) == type(object)
            print 'Block Name:\t%s' % (v.name)
            for k, v in getattr(packet, k):
    '''               

def enable_logging():

    console = StreamHandler()
    console.setLevel(DEBUG) # seems to be a no op, set it for the logger
    formatter = Formatter('%(name)-30s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    getLogger('').addHandler(console)

    # setting the level for the handler above seems to be a no-op
    # it needs to be set for the logger, here the root logger
    # otherwise it is NOTSET(=0) which means to log nothing.
    getLogger('').setLevel(DEBUG)

if __name__ == "__main__":
    main()