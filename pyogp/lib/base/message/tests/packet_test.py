"""
@file packet_test.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

import unittest

class PacketTest(unittest.TestCase):
    pass
"""
    #testing each component
    def test_freqLow(self):
        assert message_template.decodeFrequency('\xFF\xFF\x01') == 'Low', '0xFFFF01 is supposed to be "Low"'

    def test_freqMedium(self):
        assert message_template.decodeFrequency('\xFF\x01') == 'Medium', '0xFF01 is supposed to be "Medium"'

    def test_freqHigh(self):
        assert message_template.decodeFrequency('\x01') == 'High', '0x01 is supposed to be "High"'

    def test_numLow(self):
        num = message_template.decodeNum('\xFF\xFF\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'

    def test_numMedium(self):
        num = message_template.decodeNum('\xFF\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'

    def test_numHigh(self):
        num = message_template.decodeNum('\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'

    #pass cases

    def test_DecodeLow(self):
        assert message_template.decodeHeader('\xFF\xFF\x01')[0] == 'TestMessage', 'wrong message_template for 0xFFFF01: expected TestMessage'

    def test_DecodeMedium(self):
        assert message_template.decodeHeader('\xFF\x01')[0] == 'ObjectAdd', 'wrong message_template for 0xFF01: expected ObjectAdd'

    def test_DecodeHigh(self):
        assert message_template.decodeHeader('\x01')[0] == 'StartPingCheck', 'wrong message_template for 0x01: expected StartPingCheck'

    def test_DecodeLow(self):
        assert message_template.decodeHeaderPair('Low', 1)[0] == 'TestMessage', 'wrong message_template for ("Low", 1): expected TestMessage'

    def test_DecodePairMedium(self):
        assert message_template.decodeHeaderPair('Medium', 1)[0] == 'ObjectAdd', 'wrong message_template for ("Medium", 1): expected ObjectAdd'

    def test_DecodePairHigh(self):
        assert message_template.decodeHeaderPair('High', 1)[0] == 'StartPingCheck', 'wrong message_template for ("High", 1): expected StartPingCheck'

    #fail cases

    def test_DecodeLowFail(self):
        assert message_template.decodeHeader('\xFF\xFF\x01')[0] != 'TestMessage', 'wrong message_template for 0xFFFF01: expected TestMessage'

    def test_DecodeMediumFail(self):
        assert message_template.decodeHeader('\x01')[0] != 'ObjectAdd', 'wrong message_template for 0x01: expected ObjectAdd'

    def test_DecodeHighFail(self):
        assert message_template.decodeHeader('\xFF\x01')[0] != 'StartPingCheck', 'wrong message_template for 0xFF01: expected StartPingCheck'

    def test_DecodeLowFail(self):
        assert message_template.decodeHeaderPair('Medium', 1)[0] != 'TestMessage', 'wrong message_template for ("Medium", 1): expected TestMessage'

    def test_DecodePairMediumFail(self):
        assert message_template.decodeHeaderPair('High', 1)[0] != 'ObjectAdd', 'wrong message_template for ("High", 1): expected ObjectAdd'

    def test_DecodePairHighFail(self):
        assert message_template.decodeHeaderPair('Low', 1)[0] != 'StartPingCheck', 'wrong message_template for ("Low", 1): expected StartPingCheck'

    #test encode message_templateID
    def test_encodePackIDLow(self):
        pID = message_template.encodePacketID('Low', 1)
        assert pID == '\xFF\xFF\x00\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'\xFF\xFF\x00\x01'

    def test_encodePackIDMedium(self):
        pID = message_template.encodePacketID('Medium', 1)
        assert pID == '\xFF\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'\xFF\x01'

    def test_encodePackIDHigh(self):
        pID = message_template.encodePacketID('High', 1)
        assert pID == '\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'x01'

    def test_encodeHeaderLow(self):
        header = message_template.encodeHeader(message_template.LL_NONE, 1, 'Low', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01'

    def test_encodeHeaderMedium(self):
        header = message_template.encodeHeader(message_template.LL_NONE, 1, 'Medium', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\xff\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\x01'

    def test_encodeHeaderHigh(self):
        header = message_template.encodeHeader(message_template.LL_NONE, 1, 'High', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\x01'

    def test_encodeHeaderNameLow(self):
        header = message_template.encodeHeaderName(message_template.LL_NONE, 1, 'TestMessage')
        assert header == '\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01'

    def test_encodeHeaderNameMedium(self):
        header = message_template.encodeHeaderName(message_template.LL_NONE, 1, 'ObjectAdd')
        assert header == '\x00\x00\x00\x00\x01\x00\xff\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\x01'

    def test_encodeHeaderNameHigh(self):
        header = message_template.encodeHeaderName(message_template.LL_NONE, 1, 'StartPingCheck')
        assert header == '\x00\x00\x00\x00\x01\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\x01'
"""
if __name__ == "__main__":
    unittest.main()
