import json

class EchoMessage(object):
    '''Represents a message in form From:<from> To:<to> Message: <msg>,
    where 'from' and 'to' are node names'''

    def __init__(self,from_node=None,to_node=None ,msg=None):
        '''Load input paramsinto message fields'''
        self.from_node =from_node
        self.to_node   = to_node
        self.msg       = msg

    def encode(self):
        return json.dumps(self.__dict__)

    def decode(self, text):
        self.__dict__ =  json.loads(text)
if __name__ == '__main__':
    msg = EchoMessage('Starfleet','Spacedock','Launch all vessels')
    jsonText = json.dumps(msg.__dict__)
    print 'Json Encoding: '+jsonText
