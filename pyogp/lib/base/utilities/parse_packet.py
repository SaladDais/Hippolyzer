
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

#!/usr/bin/python

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..', '..')))

from optparse import OptionParser
import binascii
import re
import traceback
from pyogp.lib.base.message.udpdeserializer import UDPMessageDeserializer
from pyogp.lib.base.settings import Settings
from logging import getLogger, StreamHandler, Formatter, CRITICAL, ERROR, WARNING, INFO, DEBUG

logger = getLogger('parse_packet')
log = logger.log

class parsingStats(object):

#Todo: for this standalone script, move this class instance to global, move logging to the class itself

    def __init__(self):

        self.total = 0
        self.success = 0
        self.fail = 0
        self.packets = {}
        self.failed = []

    def addSuccess(self, name):
        self.success = self.success + 1
        if self.packets.has_key(name):
            self.packets[name] = self.packets[name] + 1
        else:
            self.packets[name] = 1

    def addFail(self, data):
        self.fail = self.fail + 1
        self.failed.append(data)

    def __repr__(self):

        string = "\n\n-----------------------------\n"
        string = string + "          Parsing Summary\n"
        string = string + "-----------------------------\n\n"
        string = string + "Successes\n\n"
        string = string + 'Parsed: %s\n\n' % (self.success)
        for k in self.packets:
            string = string + '%s: %s\n' %(k, self.packets[k])
        string = string + "\n\nFailed to Parse\n\n"
        string = string + 'Failed: %s\n\n' % (self.fail)       
        for item in self.failed:
            string = string + '%s\n' %(item)

        return string


def main():

    (options) = parse_options()

    if options.verbose: enable_logging()

    if options.file:
        stats = parsingStats()
        process_file(options, stats)
        print stats
    else:
        process_stream(options.data)

def process_file(options, stats):

    if options.wireshark:
        handle = open(options.file,"r")
        # normal hex file, 1 packet of hex per line    
        lines = handle.readlines
        handle.close()
        isSLclientpacket = False
        isSLsimpacket = False
        packetSource = ''

        if options.count > 0:
            counter = 0.0
            linecount = len(lines)
            markers = [10,20,30,40,50,60,70,80,90,100]

            log(INFO, 'Processing %s of up to %s packets' % (options.count, linecount))

        percent = 0.0
        for line in lines:
            if percent == 100: break
            if re.search('udp.srcport', line) and re.search('1300[0-9]', line):
                isSLsimpacket = True
                packetSource = 'Simulator'
                continue
            if re.search('udp.dstport', line) and re.search('1300[0-9]', line):
                isSLclientpacket = True
                packetSource = 'Client'
                continue 
            if (isSLclientpacket == True or isSLsimpacket == True):
                if re.search('field name="data"', line):
                    if options.count > 0:
                        percent = (counter/float(options.count)) * 100
                        #log(INFO, "%s percent complete... (%s of %s)" % (percent, counter, options.count))
                        if (percent) in markers:
                            log(INFO, "%s percent complete... (%s of %s)" % (int(percent), counter, options.count))
                    counter += 1
                    items = line.split()
                    process_stream(items[2][7:len(items[2])-3], packetSource, stats)
                    isSLclientpacket = False
                    isSLsimpacket = False

    else:
        handle = open(options.file,"r")
        # normal hex file, 1 packet of hex per line    
        lines = handle.readlines() 
        for line in lines:
            process_stream(line.strip())

def process_wiresharkpacket(packet):

    print packet.__dict__


def process_stream(data, source=None, stats = None):

    msg_buff = gen_message_buffer(data)

    settings = Settings()
    settings.ENABLE_DEFERRED_PACKET_PARSING = False

    if msg_buff != None:
        try:
            deserializer = UDPMessageDeserializer(settings = settings)
            packet = deserializer.deserialize(msg_buff)
            display_packet(packet, data, source)
            if stats != None:
                stats.addSuccess(packet.name)
        except Exception, e:
            print 'Unable to parse data "%s" due to: %s' % (data, e)
            traceback.print_exc()
            if stats != None:
                stats.addFail(data)
    else:
        print 'Skipping empty message buffer'

def parse_options():

    parser = OptionParser()

    #parser.add_option("-t", "--type", dest="datatype", default="hex", help="datatype to parse, default = hex")
    parser.add_option("-d", "--data", dest="data", help="data to parse")
    parser.add_option("-v", "--verbose", dest="verbose", default=True, action="store_false")
    parser.add_option("-f", "--file", dest="file", help="parse data located in file")
    parser.add_option("-w", "--wireshark", dest="wireshark", default=False, action="store_true", help="specifies file to parse is a wireshark pdml dump")
    parser.add_option("-c", "--count", dest="count", default=0, help="how many packets to process from a file")

    (options, args) = parser.parse_args()

    if options.wireshark and not options.file:
        print "Cannot parse as wireshark and not pass a file in..."
        sys.exit(-1)

    return options

def gen_message_buffer(data, datatype='hex'):

    if datatype == 'hex':
        return message_buff_from_hex(data.strip())

    return

def message_buff_from_hex(data):

    try:
        parsed = binascii.unhexlify(''.join(data.split()))
        return parsed
    except:
        print 'Error parsing data: %s' % (data)
        return None

def display_packet(packet, data, source=None):

    sourcestring = ''
    if source != None:
        sourcestring = ' (from %s)' % (source)

    print "~~~~~~~~~~~~~~~~~~~"
    print "Source data%s:" % (sourcestring)
    print data
    print "~~~~~~~~~~~~~~~~~~~"
    delim = "    "
    print 'Packet Name:%s%s' % (delim, packet.name)

    for k in packet.__dict__:

        if k == 'name': pass
        if k == 'message_data':
            print k
            for ablock in packet.blocks:
                print "%sBlock Name:%s%s" % (delim, delim, ablock)
                for somevars in packet.blocks[ablock]:

                    for avar in somevars.var_list:
                        zvar = somevars.get_variable(avar)
                        print "%s%s%s:%s%s" % (delim, delim, zvar.name, delim, zvar)

    print "~~~~~~~~~~~~~~~~~~~"

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



