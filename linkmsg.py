import json, time

class LinkMsg:
    '''LinkStateMessage, reconstituted from JSON'''

    def __init__(self, from_node = None, to_node=None) :
        self.to_node     = to_node
        self.from_node   = from_node
        self.expiration = int(time.time())+120 

    def reconstitute_(self, jsonText):
        '''Reconstitute this message from JSON text'''
        self.__dict__ = json.loads(jsonText)

    @staticmethod
    def encode(obj):
        return json.dumps(obj.__dict__)

if __name__ == "__main__":
    #demo JSON encoding
    msg = LinkMsg('salida','aspen')
    jsonText = json.dumps(msg.__dict__)
    print 'Json Encoding: '+jsonText
    newMsg= LinkMsg()
    #newMsg.reconstitute(jsonText)
    dict = json.loads(jsonText)
    print 'Reconstituted message: from: '+dict['from_node'] +' to: '+dict['to_node'] + ' expires: '+str(dict['expiration'])



