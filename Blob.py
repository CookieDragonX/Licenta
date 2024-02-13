from Object import Object

# Blob --> array of bytes

class Blob(Object):
    def __init__(self,text) -> None:
        super().__init__()
        bytes = bytearray(text.encode('utf-8'))