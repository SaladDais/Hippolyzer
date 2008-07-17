#!/usr/bin/python

import unittest
from indra.ipc import llsdhttp
from indra.base import lluuid

class RequestRezAvatarTests(unittest.TestCase):
    agent_id = '3d2b8256-12cd-40fd-abf8-6da4ad6739a2'
    regionuri = 'http://sim2.vaak.lindenlab.com:12035'
    #  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/request
    request_rez_avatar_url = regionuri + '/agent/' + agent_id + '/rez_avatar/request'
    default_arguments={
        'agent_id' : agent_id,
        'first_name': 'Leyla',
        'last_name': 'Tester',
        'age_verified' : True,
        'agent_access' : True,
        'god_level':  200,
        'identified':  True,
        'transacted': True,
        'limited_to_estate': 1,
        'sim_access' : 'Mature'
        }
    def check_successful_response(self, arguments):
        print "ARGs", arguments
        result = llsdhttp.post(self.request_rez_avatar_url, arguments)
        print "RESULT", result
        # check for existence of fields
        self.assert_(result.has_key('connect') and
                     result.has_key('rez_avatar/rez') and
                     result.has_key('sim_ip') and
                     result.has_key('sim_port') and
                     result.has_key('region_x') and
                     result.has_key('region_y') and
                     result.has_key('region_id') and
                     result.has_key('sim_access') and
                     result.has_key('seed_capability'))

        self.assertEquals(result['connect'], True)
        self.assert_(result['region_x'] < 256)
        self.assert_(result['region_x'] < 256)
        self.assert_(isUUID(result['region_id']))

    def check_failure_response(self, arguments):
        print "ARGs", arguments
        try:
            result = llsdhttp.post(self.request_rez_avatar_url, arguments)
            print "RESULT", result
        except Exception, e:
            # supposed to be error
            return

        self.assertEquals(result['connect'], False)

    def test0_simple(self):
        self.check_successful_response(self.default_arguments)

    def test1_unverified(self):
        """ Unverified agents should not be allowed """
        args = self.default_arguments
        args['age_verified'] = False
        self.check_failure_response(args)

    def test2_noaccess(self):
        """ Agents without access cannot be allowed """
        args = self.default_arguments
        args['agent_access'] = False
        self.check_failure_response(args)
        
    def test3_unidentified(self):
        """ Unidentified agents should not be allowed """
        args = self.default_arguments
        args['identified'] = False
        self.check_failure_response(args)

    def test4_godlevel(self):
        """ Gods are allowed in teen regions """
        args = self.default_arguments
        args['god_level'] = 0
        self.check_failure_response(args)

    def test5_untransacted(self):
        """ Agents not transacted are not allowed in ____ regions """
        args = self.default_arguments
        args['transacted'] = False
        self.check_failure_response(args)

    def test6_limited_estate(self):
        """ Teens limited to estate 5 cannot access adult regions """
        args = self.default_arguments
        args['limited_to_estate'] = 5
        self.check_failure_response(args)

    def test7_sim_access(self):
        """ Agents with PG access cannot access mature region """
        args = self.default_arguments
        args['sim_access'] = 'PG'
        self.check_failure_response(args)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RequestRezAvatarTests))
    return suite

if __name__ == '__main__':
    unittest.main()
