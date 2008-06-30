#!/usr/bin/python
"""
@file presence_code.py
@author Lawson English
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

from struct import *
from zerocode import  *
import md5
import xmlrpclib
import sys 
 
import re
import httplib, urllib        
from urlparse import urlparse    
import socket, sys, time
import uuid
from makepacketdict import makepacketdict
 
 
 
from datetime import datetime
 
 
mypacketdictionary = {}
outputstring = ''
ack_need_list = []

MAC = '00:00:00:00:00:00'

logoutputflag = False
 
if logoutputflag:
    temp = sys.stdout
    sys.stdout =open('alog.txt','w')
 
def login(first, last, passwd, mac):
  passwd_md5 = '$1$' + md5.new(passwd).hexdigest()
 
  uri = 'http://127.0.0.1'
  uri = 'https://login.aditi.lindenlab.com/cgi-bin/login.cgi'
  s = xmlrpclib.ServerProxy(uri)
 
  login_details = {
    'first': first,
    'last': last,
    'passwd': passwd_md5,
    #'start': 'last',
    'start': 'uri:Hazzard County&141&33&35',
    'major': '1',
    'minor': '18',
    'patch': '5',
    'build': '3',
    'platform': 'Win',
    'mac': mac,
    'options': [],
    'user-agent': 'sl.py 0.1',
    'id0': '',
    'agree_to_tos': '',
    'viewer_digest': '09d93740-8f37-c418-fbf2-2a78c7b0d1ea',
    'version': '1.0.0'
  }
  results = s.login_to_simulator(login_details)
  print results
 
  return results
 
 
 
 
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
 
def establishpresence(host, port, circuit_code):
 
 
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
 
    buf = 100
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
        t = datetime.now()
        t.strftime("%H:%M:%S")
 
 
 
        if not data:
            print "Client has exited!"
 
            break
        else:
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
                        myentry = mypacketdictionary[("Low",int("0x"+ByteToHex(ID[2:4]).replace(' ', ''),16))]
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
    sock.close()
    print "final number of trusted messages =", trusted_count
 
    return
 
 
 
 
result = login("Enusbot1", "LLQABot", "lindentest", MAC)
 
mypacketdictionary = makepacketdict()
 
myhost = result["sim_ip"]
myport = result["sim_port"]
mycircuit_code = result["circuit_code"]
 
establishpresence(myhost, myport, mycircuit_code)
 
#cap_out = get_caps(result,"seed_capability", ["ChatSessionRequest"])
