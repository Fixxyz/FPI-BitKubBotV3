from BL.LineNotifyService import *

def test_SendLineNotify():
    assert "200" in SendLineNotify("test").lower() 
