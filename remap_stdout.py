import logging

class RemapStdout:
    def __init__(self, Output, name, fname ):
        self.name = name
        self.fname = fname
        self.Output = Output # original output
        self.buf = ''

        #self.formatter = logging.Formatter('%(asctime)s (%(threadName)-15s %(name)s) %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s (%(threadName)s %(name)s) %(levelname)s - %(message)s')

        self.fh = logging.FileHandler( fname )
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.formatter)

        self.sh = logging.StreamHandler( Output )
        self.sh.setLevel(logging.DEBUG)
        self.sh.setFormatter(self.formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.sh)


    # do the actual writing
    def write(self, data):
        self.buf += data

        if( self.buf[-1] == "\n" ):
            self.flush()

    def flush(self):
        if( self.name == 'stderr' ):
            self.logger.error( self.buf.rstrip() )
        else:
            self.logger.info( self.buf.rstrip() )

        self.buf = ''

