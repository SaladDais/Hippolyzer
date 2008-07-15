import unittest
import packet

class PacketTest(unittest.TestCase):

    #testing each component
    def test_freqLow(self):
        assert packet.decodeFrequency('\xFF\xFF\x01') == 'Low', '0xFFFF01 is supposed to be "Low"'

    def test_freqMedium(self):
        assert packet.decodeFrequency('\xFF\x01') == 'Medium', '0xFF01 is supposed to be "Medium"'

    def test_freqHigh(self):
        assert packet.decodeFrequency('\x01') == 'High', '0x01 is supposed to be "High"'

    def test_numLow(self):
        num = packet.decodeNum('\xFF\xFF\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'

    def test_numMedium(self):
        num = packet.decodeNum('\xFF\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'
            
    def test_numHigh(self):
        num = packet.decodeNum('\x01')
        assert num == 1, 'Outcome: ' + str(num) + ' Expected: 1'
        
    #pass cases
    
    def test_DecodeLow(self):
        assert packet.decodeHeader('\xFF\xFF\x01')[0] == 'TestMessage', 'wrong packet for 0xFFFF01: expected TestMessage'

    def test_DecodeMedium(self):
        assert packet.decodeHeader('\xFF\x01')[0] == 'ObjectAdd', 'wrong packet for 0xFF01: expected ObjectAdd'

    def test_DecodeHigh(self):
        assert packet.decodeHeader('\x01')[0] == 'StartPingCheck', 'wrong packet for 0x01: expected StartPingCheck'

    def test_DecodeLow(self):
        assert packet.decodeHeaderPair('Low', 1)[0] == 'TestMessage', 'wrong packet for ("Low", 1): expected TestMessage'

    def test_DecodePairMedium(self):
        assert packet.decodeHeaderPair('Medium', 1)[0] == 'ObjectAdd', 'wrong packet for ("Medium", 1): expected ObjectAdd'

    def test_DecodePairHigh(self):
        assert packet.decodeHeaderPair('High', 1)[0] == 'StartPingCheck', 'wrong packet for ("High", 1): expected StartPingCheck'

    #fail cases

    def test_DecodeLowFail(self):
        assert packet.decodeHeader('\xFF\xFF\x01')[0] != 'TestMessage', 'wrong packet for 0xFFFF01: expected TestMessage'

    def test_DecodeMediumFail(self):
        assert packet.decodeHeader('\x01')[0] != 'ObjectAdd', 'wrong packet for 0x01: expected ObjectAdd'

    def test_DecodeHighFail(self):
        assert packet.decodeHeader('\xFF\x01')[0] != 'StartPingCheck', 'wrong packet for 0xFF01: expected StartPingCheck'

    def test_DecodeLowFail(self):
        assert packet.decodeHeaderPair('Medium', 1)[0] != 'TestMessage', 'wrong packet for ("Medium", 1): expected TestMessage'

    def test_DecodePairMediumFail(self):
        assert packet.decodeHeaderPair('High', 1)[0] != 'ObjectAdd', 'wrong packet for ("High", 1): expected ObjectAdd'

    def test_DecodePairHighFail(self):
        assert packet.decodeHeaderPair('Low', 1)[0] != 'StartPingCheck', 'wrong packet for ("Low", 1): expected StartPingCheck'

    #test encode packetID
    def test_encodePackIDLow(self):
        pID = packet.encodePacketID('Low', 1)
        assert pID == '\xFF\xFF\x00\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'\xFF\xFF\x00\x01'
        
    def test_encodePackIDMedium(self):
        pID = packet.encodePacketID('Medium', 1)
        assert pID == '\xFF\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'\xFF\x01'

    def test_encodePackIDHigh(self):
        pID = packet.encodePacketID('High', 1)
        assert pID == '\x01', 'Outcome: ' + repr(pID) + ' Expected: ' + r'x01'

    def test_encodeHeaderLow(self):
        header = packet.encodeHeader(packet.LL_NONE, 1, 'Low', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01'
        
    def test_encodeHeaderMedium(self):
        header = packet.encodeHeader(packet.LL_NONE, 1, 'Medium', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\xff\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\x01'

    def test_encodeHeaderHigh(self):
        header = packet.encodeHeader(packet.LL_NONE, 1, 'High', 1)
        assert header == '\x00\x00\x00\x00\x01\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\x01'

    def test_encodeHeaderNameLow(self):
        header = packet.encodeHeaderName(packet.LL_NONE, 1, 'TestMessage')
        assert header == '\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\xff\x00\x01'
        
    def test_encodeHeaderNameMedium(self):
        header = packet.encodeHeaderName(packet.LL_NONE, 1, 'ObjectAdd')
        assert header == '\x00\x00\x00\x00\x01\x00\xff\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\xff\x01'

    def test_encodeHeaderNameHigh(self):
        header = packet.encodeHeaderName(packet.LL_NONE, 1, 'StartPingCheck')
        assert header == '\x00\x00\x00\x00\x01\x00\x01', 'Outcome: ' + repr(header) + ' Expected: ' + r'\x00\x00\x00\x00\x01\x00\x01'

if __name__ == "__main__":
    unittest.main()
