import ZServer
import Zope
import unittest, string
from Products.CMFCalendar.Event import *
from DateTime import DateTime

class TestEvent(unittest.TestCase):
    def test_new(self):
        event = Event('test')
        assert event.getId() == 'test'
        assert not event.Title()
    
    def test_edit(self):
        event = Event('editing')
        event.edit( title='title'
                  , description='description'
                  , eventType=( 'eventType', )
                  , effectiveDay=1
                  , effectiveMo=1
                  , effectiveYear=1999
                  , expirationDay=12
                  , expirationMo=31
                  , expirationYear=1999
                  , start_time="00:00"
                  , startAMPM="AM"
                  , stop_time="11:59"
                  , stopAMPM="PM"
                  )
        assert event.Title() == 'title'
        assert event.Description() == 'description'
        assert event.Subject() == ( 'eventType', ), event.Subject()
        assert event.effective_date == None 
        assert event.expiration_date == None 
        assert event.end() == DateTime('1999/12/31 23:59')
        assert event.start() == DateTime('1999/01/01 00:00')
        assert not event.contact_name

    def test_puke(self):
        event = Event( 'shouldPuke' )
        self.assertRaises( DateTime.DateError
                         , event.edit
                         , effectiveDay=31
                         , effectiveMo=2
                         , effectiveYear=1999
                         , start_time="00:00"
                         , startAMPM="AM"
                         )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestEvent ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
