import threading, time, socket, select, traceback, pprint, Queue

from defs import *
import packet


class client:
    def __init__( self, server, port, msg_action = None ):
        self.sock = None
        self.server = server
        self.port = port
        self.msg_action = msg_action
        self.get_pack_state = False
        self.stop_tok = threading.Event()
        self.timer = 0
        self.last_packet_time = 0
        self.sent_poll = False
        self.ng_pkt = packet.ng_packetizer()

    def want_pack_state( self, want = True ):
        self.get_pack_state = bool(want)

    def stop( self ):
        self.stop_tok.set()
        self.close()

    def run_forever( self ):
        while not self.stop_tok.is_set():
            try:
                self.mainloop()
            except:
                traceback.print_exc()
                print 'Main Loop crashed!'

                try:
                    self.close()
                except:
                    pass

                self.sock = None

    def mainloop( self ):
        self.connect()

        while not self.stop_tok.is_set():
            if self.sock is None:
                if( self.timer < time.time() ):
                    time.sleep( 5 )
                    continue

                self.connect()

                if self.sock is None:
                    time.sleep( 5 )
                    continue

            want = self.ng_pkt.want_bytes()

            while( want == 0 ):
                self.handle_packet( self.ng_pkt.decode() )
                want = self.ng_pkt.want_bytes()

            try:
                buf = self.sock.recv( want )
            except socket.timeout:
                if( (time.time() - self.last_packet_time) > 60 ):
                    print 'Connection dropped!'
                    self.close()
                elif( (time.time() - self.last_packet_time) > 30 ):
                    self.send_poll()
                else:
                    print 'tick'

                continue
            except:
                traceback.print_exc()
                print 'Connection dropped!'
                self.close()
                continue

            if( len(buf) < 1 ):
                print 'Connection closed!'
                self.close()
            else:
                self.ng_pkt.accumulate( buf )
                # the next trip through the loop will process the data/packet


    def connect( self ):
        print 'Attempting to connect to', self.server
        self.close()
        self.timer = time.time() + 30

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout( 5 )
            self.sock.connect( (self.server, self.port) )
            self.connection_opened()
        except:
            traceback.print_exc()
            print 'Connection Failed!'
            self.close()

        return


    def close( self ):
        self.last_packet_time = 0
        self.sent_poll = False
        self.ng_pkt.clear()

        if( self.sock is not None ):
            try:
                self.sock.close()
                print 'Connection Closed'
            finally:
                self.sock = None

        self.timer = time.time() + 10

    def connection_opened( self ):
        print 'Connection to', self.server, 'opened, requesting event auto-send'
        self.last_packet_time = time.time()
        self.send( self.ng_pkt.encode_byte( CMD_TCP_SET_CLIENT_AUTO_SEND, AUTO_SEND_SERVER_MODE ) )
        self.send( self.ng_pkt.encode_byte( CMD_TCP_SET_CLIENT_AUTO_SEND, AUTO_SEND_GAME_EVENTS ) )
        self.send( self.ng_pkt.get_gameserver_mode() )

        #if( self.get_pack_state ):
        self.send( self.ng_pkt.get_all_pack_status() )

        if( self.sock is not None ):
            print 'Requested OK.'

    def send( self, data ):
        self.sent_poll = False

        if( self.sock is None ):
            print 'No connection, not sending'
            return

        tosend = len(data)
        print 'sending', tosend, 'bytes to the server'

        while( tosend > 0 ):
            try:
                sent = self.sock.send( data )
            except:
                traceback.print_exc()
                sent = 0

            if( sent == 0 ):
                print 'Send Failed!  Closing connection'
                self.close()
                return

            tosend -= sent

    def send_poll( self ):
        if( self.sent_poll ):
            return

        print 'Polling for server mode'
        self.send( self.ng_pkt.get_gameserver_mode() )
        self.sent_poll = True

        if( self.get_pack_state ):
            self.send( self.ng_pkt.get_all_pack_status() )


    def handle_packet( self, pkt ):
        if pkt is None:
            print 'Packet is None!'
            return

        self.sent_poll = False
        self.last_packet_time = time.time()

        if( self.msg_action is None ):
            print 'Got Packet:'
            pprint.pprint( pkt )

        elif( isinstance(self.msg_action, Queue.Queue) ):
            try:
                self.msg_action.put( pkt, True, 1 )
            except:
                traceback.print_exc()
        elif( callable( self.msg_action ) ):
            self.msg_action( pkt )
        else:
            print 'Invalid packet handler!', self.msg_action

