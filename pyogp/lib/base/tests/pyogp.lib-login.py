#!/usr/bin/python
"""
@file pyogp.lib-login.py
@author Linden Lab
@date 2008-06-13
@brief Iniitializes path directories

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
$/LicenseInfo$
"""

import sys, struct
import os.path
import urllib2
import md5
import xmlrpclib
import re
from urlparse import urlparse    
import socket, sys, time
import uuid
from  struct import *
from optparse import OptionParser
import pprint
 
from datetime import datetime


if os.path.exists("../setup_path.py"):
	execfile("../setup_path.py")

# linden provided libs
from indra.base import llsd
from indra.ipc import llsdhttp
from indra.base import lluuid

# lib classes
from pyogp.lib.agent import Agent
from pyogp.client.ogplogin import OGPLogin
from pyogp.lib.capabilities import Capabilities

# Sai's helpers
from makepacketdict import makepacketdict  
from zerocode import *

# defaults for the purpose of this test script
debug = True

mypacketdictionary = {}
outputstring = ''
ack_need_list = []

def main():

    (options) = process_options()

    agent = Agent()

    agent.setLoginParams(options.firstname, options.lastname, options.password, None, options.loginuri, options.regionuri)
    
    if debug:
        print 'Posting the following llsd to ' + agent.loginuri
        print agent.getLoginParams()

    login = OGPLogin(agent)    
    result = login.login()

    if result == None:
        print 'Couldn"t log in.'
        return

    myhost = result['sim_ip']
    myport = result['sim_port']
    mycircuit_code = result['circuit_code']

    establishpresence(myhost, myport, mycircuit_code, result)
    
    #cap_out = get_caps(result,"seed_capability", ["ChatSessionRequest"])
   
def process_options():

    parser = OptionParser(usage="pyogp.lib-login.py --firstname [firstname] --lastname [lastname] --password [password]")
    parser.add_option("--firstname", dest="firstname", help="firstname of the agent to login to the agent domain")
    parser.add_option("--lastname", dest="lastname", help="lastname")
    parser.add_option("--password", dest="password", help="password - not md5 for now")
    parser.add_option("--md5pass", dest="md5pass", help="inactive md5 placeholder", default=None)
    parser.add_option("--loginuri", dest="loginuri", help="loginuri to authenticate against", default='https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi')
    parser.add_option("--regionuri", dest="regionuri", help="regionuri of the simulator to connect to", default='http://sim1.vaak.lindenlab.com:13000')   
    options, args = parser.parse_args()
    
    if not options.firstname:
        print "ERROR: --firstname is required"
        print parser.get_usage()
        sys.exit(-1)

    if not options.lastname:
        print "ERROR: --lastname is required"
        print parser.get_usage()
        sys.exit(-1)

    if not options.password:
        print "ERROR: --password is required"
        print parser.get_usage()
        sys.exit(-1)


    return options    
def get_caps(results,cap_key, request_keys):
 
  _, netloc, path, _, _, _ = urlparse(results[cap_key])
 
  params = "<llsd><array><string>"+ request_keys[0]+"</string></array></llsd>"
  headers = {"content-type": "application/xml"}
  conn = httplib.HTTPSConnection(netloc)
 
  conn.request("POST", path, params, headers)
  response = conn.getresponse()
 
 
  data = response.read()
  conn.close()
  return data
 
def ExtractCap(cap_result):
  trim_xml = re.compile(r"<key>([a-zA-Z_]+)</key><string>([a-zA-Z_:/0-9-.]+)</string>")
  new_key = trim_xml.search(cap_result).group(1)
  new_cap = trim_xml.search(cap_result).group(2)
  return new_key, new_cap
 
 
 
def scheduleacknowledgemessage(data):
    if not (ord(data[0])&0x40):
        print "OOOPS! Got asked to ack a message that shouldn't be acked"
 
        return
    else:
        ID = data[1:5]
        if (ord(data[0])&0x40) & 0x80: ID = zero_decode_ID(ID)
        ack_need_list.append(unpack(">L",ID)[0])
        #ack_need_list.append(unpack(">L",data[1:5])[0])
        #print "ack needed","insdie schedule ack_need_list", ack_need_list
 
 
    return
 
def packacks():
    acksequence = ""
    for msgnum in ack_need_list:
        acksequence = acksequence + pack("<L", msgnum)
 
 
    return acksequence
 
#def sendacks():
 #   if len(ack_need_list)>0:
 
 
#===============================================================================
# {
#    UUIDNameRequest Low NotTrusted Unencoded
#    {
#        UUIDNameBlock    Variable
#        {    ID            LLUUID    }
#    }
# }
#===============================================================================
 
def sendUUIDNameRequest(sock, port, host, currentsequence,aUUID):
 
    packed_data = ""
    fix_ID = int("0xffff0000",16)+ 235
    data_header = pack('>BLB', 0x00,currentsequence,0x00) 
 
 
    for i in range(len(aUUID)):
        packed_data = packed_data+uuid.UUID(aUUID[i]).bytes
 
    packed_data = data_header + pack("L",fix_ID) + pack(">B",len(aUUID)) + packed_data
 
    sock.sendto(packed_data, (host, port)) 
    return              
 
def sendRegionHandshakeReply(sock, port, host, currentsequence,agentUUID,sessionUUID):
    packed_data = ""
 
    low_ID = "0xffff00%2x" % 149
    data_header = pack('>BLB', 0x00,currentsequence,0x00)
    packed_data = packed_data+uuid.UUID(agentUUID).bytes+uuid.UUID(sessionUUID).bytes+ pack(">L",0x00)
    packed_data = data_header + pack(">L",int(low_ID,16))+packed_data
    sock.sendto(packed_data, (host, port)) 
    #print "RegionHandshakeReply", ByteToHex(packed_data)
    return
 
 
 
def sendAgentUpdate(sock, port, host, currentsequence, result):
 
#AgentUpdate
 
    tempacks = packacks()
    del ack_need_list[0:]
    if tempacks == "": 
        flags = 0x00
    else:
        flags = 0x10
 
    #print "tempacks is:", ByteToHex(tempacks)  
 
    data_header = pack('>BLB', flags,currentsequence,0x00)
    packed_data_message_ID = pack('>B',0x04)
    packed_data_ID = uuid.UUID(result["agent_id"]).bytes + uuid.UUID(result["session_id"]).bytes
    packed_data_QuatRots = pack('<ffff', 0.0,0.0,0.0,0.0)+pack('<ffff', 0.0,0.0,0.0,0.0)  
    packed_data_State = pack('<B', 0x00)
    packed_data_Camera = pack('<fff', 0.0,0.0,0.0)+pack('<fff', 0.0,0.0,0.0)+pack('<fff', 0.0,0.0,0.0)+pack('<fff', 0.0,0.0,0.0)
    packed_data_Flags = pack('<fLB', 0.0,0x00,0x00)
 
    encoded_packed_data = zero_encode(packed_data_message_ID+packed_data_ID+packed_data_QuatRots+packed_data_State+packed_data_Camera+packed_data_Flags)
 
    packed_data = data_header + encoded_packed_data+tempacks
 
   # print "sending AgentUpdate to server",ByteToHex(packed_data_header+zero_decode(encoded_packed_data)+ tempacks)
 
    sock.sendto(packed_data, (host, port))
    return
 
def sendCompletePingCheck(sock, port, host, currentsequence,data,lastPingSent):
#    print "data from PingCHeck", ByteToHex(data)
 
    data_header = pack('>BLB', 0x00,currentsequence,0x00)
    packed_data_message_ID = pack('>B',0x02)
    packed_data = data_header + packed_data_message_ID+pack('>B', lastPingSent)
    print "CompletePingCheck packet sent:", ByteToHex(packed_data)
    sock.sendto(packed_data, (host, port))
 
    return
 
def sendPacketAck(sock, port, host,currentsequence):
 
    tempacks = packacks()
    templen = len(ack_need_list)
    del ack_need_list[0:]
    data_header = pack('>BLB',0x00,currentsequence,0x00) 
    packed_data_message_ID = pack('>L',0xFFFFFFFB)
    packed_ack_len = pack('>B',templen)
 
    packed_data = data_header + packed_data_message_ID + packed_ack_len + tempacks
#===============================================================================
#    t = datetime.now()
#    t.strftime("%H:%M:%S")
#    ti = "%02d:%02d:%02d.%06d" % (t.hour,t.minute,t.second,t.microsecond)
#    print ti, "PacketAck packet sent:", ByteToHex(packed_data)
#===============================================================================
    sock.sendto(packed_data, (host, port))
    return
 
def sendLogoutRequest(sock, port, host,seqnum,aUUID,sUUID):
    packed_data = ""
    packed_data_message_ID = pack('>L',0xffff00fc)
    data_header = pack('>BLB', 0x00,seqnum,0x00)
    packed_data = packed_data+uuid.UUID(aUUID).bytes+uuid.UUID(sUUID).bytes+ pack(">L",0x00)
 
    packed_data = data_header + packed_data_message_ID + packed_data
    sock.sendto(packed_data, (host, port))
    return
 
 
def establishpresence(host, port, circuit_code, result): 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Sending packet UseCircuitCode <-- Inits the connection to the sim.
    data = pack('>BLBL',0x00,0x01,00,0xffff0003) + pack('<L',circuit_code) + uuid.UUID(result["session_id"]).bytes+uuid.UUID(result["agent_id"]).bytes
    sock.sendto(data, (host, port))
 
#ISending packet CompleteAgentMovement <-- establishes the agent's presence
    data = pack('>BLBL',0x00,0x02,00,0xffff00f9) + uuid.UUID(result["agent_id"]).bytes + uuid.UUID(result["session_id"]).bytes + pack('<L', circuit_code)
    sock.sendto(data, (host, port))
 
    sendAgentUpdate(sock, port, host, 3, result)
    aUUID = [result["agent_id"]]
    sendUUIDNameRequest(sock, port, host, 4,aUUID)
#
 
    buf = 10000
    i = 0
    trusted_count = 0
    ackable = 0
    trusted_and_ackable = 0
    ack_need_list_changed = False
    seqnum = 5
    lastPingSent = 0 
    trusted = 0
    while 1:
        if ack_need_list_changed:
            ack_need_list_changed = False
            seqnum = seqnum + 1
            sendPacketAck(sock, port, host,seqnum)
            #sendAgentUpdate(sock, port, host, seqnum, result)
            seqnum += 1
        #sendacks()
        i = i + 1
        data,addr = sock.recvfrom(buf)
        #print data
        t = datetime.now()
        t.strftime("%H:%M:%S")
        #break when we have done enough testing
        #if i > 30:
        #    break
 
        ''' 
        if not data:
            print "Client has exited!"
 
            break
        else:
            pass
            test =  ByteToHex(data).split()
            #print test
            ID = data[6:12]
            #print "ID =", ByteToHex(ID) 
            if (ord(data[0])&0x80): 
                ID = zero_decode_ID(data[6:12])
 
            if (ord(data[0])&0x40): 
                scheduleacknowledgemessage(data); 
                ack_need_list_changed = True
            #print "ID =", ByteToHex(ID) 
            #print "ID =", unpack(">L", ID[:4])
            if ID[0] == '\xFF':
                if ID[1] == '\xFF':
                    if ID[2] == '\xFF':
                        myentry = mypacketdictionary[("Fixed" , "0x"+ByteToHex(ID[0:4]).replace(' ', ''))]
                        if myentry[1] == "Trusted":
                            trusted += 1;
                        ti = "%02d:%02d:%02d.%06d" % (t.hour,t.minute,t.second,t.microsecond)
                        print ti, "Message #", i, "trusted count is", trusted,"Flags: 0x" + test[0], myentry,  "sequence #", unpack(">L",data[1:5])
 
                        #if myentry[1] == "Trusted": trusted_count = trusted_count +1;print "number of trusted messages =", trusted_count
                        #if (ord(data[0])&0x40) and (myentry[1] == "Trusted"): trusted_and_ackable = trusted_and_ackable + 1; print "trusted_and_ackable =", trusted_and_ackable
                        #if (ord(data[0])&0x40): ackable = ackable + 1; print "number of ackable messages = ", ackable
                    else:
                        myentry = mypacketdictionary[("Low",int("0x"+ByteToHex(ID[2:4]).replace(' ', ''),16))] # ,16
                        if myentry[1] == "Trusted":
                            trusted += 1;
                        ti = "%02d:%02d:%02d.%06d" % (t.hour,t.minute,t.second,t.microsecond)
                        print ti, "Message #", i,"trusted count is", trusted,"Flags: 0x" + test[0], myentry,   "sequence #", unpack(">L",data[1:5])
                        if myentry[0] == "UUIDNameReply":
                            pass
                            #print ByteToHex(data)
                            #print data[:28]
                            #print data[28:36],data[38:45]
                        elif myentry[0] == "RegionHandshake":
                            sendRegionHandshakeReply(sock, port, host, seqnum,result["agent_id"],result["session_id"])
                            seqnum += 1
 
                        #if myentry[1] == "Trusted": trusted_count = trusted_count +1;print "number of trusted messages =", trusted_count
                        #if (ord(data[0])&0x40) and (myentry[1] == "Trusted"): trusted_and_ackable = trusted_and_ackable + 1; print "trusted_and_ackable =", trusted_and_ackable
                       #if (ord(data[0])&0x40): ackable = ackable + 1; print "number of ackable messages = ", ackable
                else:
                    myentry = mypacketdictionary[("Medium", int("0x"+ByteToHex(ID[1:2]).replace(' ', ''),16))]
                    if myentry[1] == "Trusted":
                        trusted += 1;
                    ti = "%02d:%02d:%02d.%06d" % (t.hour,t.minute,t.second,t.microsecond)
                    print ti, "Message #", i,"trusted count is", trusted,"Flags: 0x" + test[0], myentry,  "sequence #", unpack(">L",data[1:5])
 
 
                    #if myentry[1] == "Trusted": trusted_count = trusted_count +1;print "number of trusted messages =", trusted_count
                    #if (ord(data[0])&0x40) and (myentry[1] == "Trusted"): trusted_and_ackable = trusted_and_ackable + 1; print "trusted_and_ackable =", trusted_and_ackable
                    #if (ord(data[0])&0x40): ackable = ackable + 1; print "number of ackable messages = ", ackable
            else:
                myentry = mypacketdictionary[("High", int("0x"+ByteToHex(ID[0]), 16))]
                if myentry[0] == "StartPingCheck": 
                    print "data from StartPingCheck", test
                    sendCompletePingCheck(sock, port, host, seqnum,data,lastPingSent)
                    lastPingSent = lastPingSent+  1
                    seqnum = seqnum + 1
 
                if myentry[1] == "Trusted":
                    trusted += 1;   
                ti = "%02d:%02d:%02d.%06d" % (t.hour,t.minute,t.second,t.microsecond)
 
                print ti, "Message #", i,"trusted count is", trusted,"Flags: 0x" + test[0], myentry,   "sequence #", unpack(">L",data[1:5])
 
                #if myentry[1] == "Trusted": trusted_count = trusted_count +1;print "number of trusted messages =", trusted_count
                #if (ord(data[0])&0x40) and (myentry[1] == "Trusted"): trusted_and_ackable = trusted_and_ackable + 1; print "trusted_and_ackable =",  trusted_and_ackable
                #if (ord(data[0])&0x40): ackable = ackable + 1; print "number of ackable messages = ", ackable
    '''
    sendLogoutRequest(sock, port, host,seqnum,myAgentID,mySessionID)
 
    sock.close()
    print "final number of trusted messages =", trusted_count
 
    return


if __name__ == "__main__":
    main()

