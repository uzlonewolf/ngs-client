import threading, time, socket, select, traceback, pprint, Queue, binascii

from defs import *
import packet


class client:
    def __init__( self, server, port ):
        self.sock = None
        self.server = server
        self.port = port
        self.get_pack_state = False
        self.timer = 0
        self.last_packet_time = 0
        self.next_game_state_time = 0
        self.next_pack_request_time = 0
        self.sent_poll = False
        self.ng_pkt = packet.ng_packetizer()
        self.server_state = None
        self.was_open = False

        self.stop_tok = None
        self.print_hex = False
        self.on_message = None
        self.on_connect = None
        self.on_close = None

    def want_pack_state( self, want = True ):
        self.get_pack_state = bool(want)

    def stop( self ):
        self.stop_tok.set()
        self.close()

    def run_forever( self ):
        if self.stop_tok is None:
            self.stop_tok = threading.Event()

        while not self.stop_tok.is_set():
            try:
                self.mainloop()
            except (SystemExit, KeyboardInterrupt):
                print 'run_forever() needs to exit!'
                self.stop()
                break
            except:
                traceback.print_exc()
                print 'Main Loop crashed!'

                try:
                    self.close()
                except:
                    pass

                self.sock = None

    def mainloop( self ):
        if self.stop_tok is None:
            self.stop_tok = threading.Event()

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

            if( self.get_pack_state and (self.next_pack_request_time <= time.time()) ):
                #self.send( self.ng_pkt.get_all_pack_status() )
                #self.next_pack_request_time += 30 # the time will get reset when response is received
                self.send_poll()

            want = self.ng_pkt.want_bytes()

            while( want == 0 ):
                self.handle_packet( self.ng_pkt.decode() )
                want = self.ng_pkt.want_bytes()

            try:
                buf = self.sock.recv( want )
                if( self.print_hex ):
                    print 'recv\'d:', binascii.hexlify( buf )
            except (SystemExit, KeyboardInterrupt):
                print 'Client thread needs to exit!'
                self.stop()
                break
            except socket.timeout:
                if( (time.time() - self.last_packet_time) > 60 ):
                    print 'Connection dropped!'
                    self.close()
                elif( (time.time() - self.last_packet_time) > 30 ):
                    self.next_game_state_time = 0
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
            self.sock.settimeout( 1 )
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

        if( self.was_open and callable( self.on_close ) ):
	    print( 'Calling on_close()' )
            self.on_close( self )
            self.was_open = False


    def connection_opened( self ):
        print 'Connection to', self.server, 'opened, requesting event auto-send'
        self.was_open = True
        self.last_packet_time = time.time()
        self.next_pack_request_time = time.time() + 10
        self.send( self.ng_pkt.encode_byte( CMD_TCP_SET_CLIENT_AUTO_SEND, AUTO_SEND_SERVER_MODE ) )
        self.send( self.ng_pkt.encode_byte( CMD_TCP_SET_CLIENT_AUTO_SEND, AUTO_SEND_GAME_EVENTS ) )
        self.send( self.ng_pkt.get_gameserver_mode() )

        if( self.get_pack_state ):
            self.send( self.ng_pkt.get_all_pack_status() )

        if( self.sock is not None ):
            print 'Requested OK.'
            if( callable( self.on_connect ) ):
                print( 'Calling on_connect()' )
                self.on_connect( self )

    def send( self, data ):
        self.sent_poll = False

        if( self.sock is None ):
            print 'No connection, not sending'
            return

        tosend = len(data)
        if( self.print_hex ):
            print 'sending', tosend, 'bytes to the server:', binascii.hexlify( data )
        else:
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
        #if( self.sent_poll ):
        #    return

        if( self.next_game_state_time <= time.time() ):
            print 'Polling for server mode'
            self.send( self.ng_pkt.get_gameserver_mode() )
            self.next_game_state_time = time.time() + 5
            self.on_poll( self )

        if( self.get_pack_state ):
            self.send( self.ng_pkt.get_all_pack_status() )
            self.next_pack_request_time = time.time() + 35

        self.sent_poll = True

    def handle_packet( self, pkt ):
        if pkt is None:
            print 'Packet is None!'
            return

        self.sent_poll = False
        self.last_packet_time = time.time()

        if( pkt.is_server_mode ):
            self.server_state = pkt.data
            self.next_game_state_time = time.time() + 5
        elif( pkt.is_pack_status ):
            if( self.server_state and self.server_state.mode == SERVER_MODE_RUNNING ):
                self.next_pack_request_time = time.time() + 1
            else:
                self.next_pack_request_time = time.time() + 6

        if( self.on_message is None ):
            print 'Got Packet:'
            pprint.pprint( pkt )

        elif( isinstance(self.on_message, Queue.Queue) ):
            try:
                self.on_message.put( pkt, True, 1 )
            except:
                traceback.print_exc()
        elif( callable( self.on_message ) ):
            self.on_message( pkt )
        else:
            print 'Invalid packet handler!', self.on_message

