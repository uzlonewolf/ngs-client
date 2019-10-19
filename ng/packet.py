import struct

from defs import *

class ng_packet:
    length = 0
    command = 0
    is_player_event = False
    is_pack_status = False
    is_server_mode = False
    data = None

    def __iter__(self):
        for k, v in vars(self).iteritems():
            if( k == 'data' ):
                yield k, dict(v)
            elif( k == 'command' ):
                yield k, get_var_name( v, 'CMD_TCP_' )
            else:
                yield k, v

class ng_player_event:
    event_idx     = 0   # database index number
    event_type    = 0
    player_id     = 0
    player_team   = 0
    score_applies = 0
    score         = 0
    rawdata       = [ 0, 0, 0, 0, 0, 0 ]

    player_tag    = False
    player_fired  = False
    base_hit      = False

    event_data    = None

    def __iter__(self):
        for k, v in vars(self).iteritems():
            if( k == 'event_data' ):
                yield k, dict(v)
            elif( k == 'event_type' ):
                yield k, get_var_name( v, 'PLAYER_EVENT_' )
            elif( k == 'score_applies' ):
                yield k, get_var_name( v, 'PLAYER_EVENT_SCORE_APPLIES_' )
            #elif( k == 'player_team' ):
            #    yield k, get_var_name( v, 'GAME_TEAM_' )
            elif( k == 'rawdata' ):
                yield k, str(v)
            else:
                yield k, v

class ng_player_event_tag:
    player_got_tagged      = False
    player_tagged_opponent = False

    weapon   = 0
    level    = 0
    tag_type = 0
    health   = 0

    opponent_id   = 0
    opponent_team = 0

    def __iter__(self):
        return vars(self).iteritems()

class ng_player_event_base:
    base_destroyed = False

    base_id   = None
    base_team = 0

    base_off_time  = 0 # destroyed time, or reset time after hit but not destroyed
    base_hit_time  = 0 # base will reset if it hasn't been hit again in this time

    def __iter__(self):
        return vars(self).iteritems()

class ng_player_event_trigger:
    shots_fired     = 0
    power_remaining = 0

    def __iter__(self):
        return vars(self).iteritems()

class ng_server_mode:
    mode = 0
    time_remaining = 0
    mode_data = 0

    def __iter__(self):
        for k, v in vars(self).iteritems():
            if( k == 'mode' ):
                yield k, get_var_name( v, 'SERVER_MODE_' )
            else:
                yield k, v

class ng_pack_status_pkt:
    num_packs = 0
    packs = { }

    def __iter__(self):
        #yield 'packs', { i : dict(self.packs[i]) for i in range( len(self.packs) ) }
        for k, v in vars(self).iteritems():
            if( k == 'packs' ):
                yield 'packs', { i : dict(self.packs[i]) for i in v }
            else:
                yield k, v

class ng_pack_status:
    team  = 0
    flags = 0
    state = 0
    data  = 0

    def flag( self, flag_to_check ):
        return ((self.flags & flag_to_check) == flag_to_check)

    def __iter__(self):
        return vars(self).iteritems()


class ng_data:
    typ = None
    byts = 1
    data = 0

class ng_packetizer:
    def __init__( self ):
        self.buf = '' # buffer for decoding

    def clear( self ):
        self.buf = ''


    ######################
    # Encoding functions #
    ######################

    def packetize( self, cmd, data = None ):

        if( data is None ):
            length = 0
        else:
            length = len(data)

            if( length < 0 ):
                raise ValueError('packetize: length cannot be negative!')

        # unsigned short int
        buf = struct.pack( '<H', length )
        buf += chr( cmd )

        if( data is not None ):
            buf += data

        return buf

    def stringize( self, data ):
        buf = ''

        for d in data:
            if( d.typ is not None ):
                buf += struct.pack( d.typ, d.data )
            elif( d.byts == 0 ): # Bool
                buf += struct.pack( '<?', d.data )
            elif( d.byts == 2 ): # unsigned short int
                buf += struct.pack( '<H', d.data )
            elif( d.byts == 4 ): # signed int
                buf += struct.pack( '<i', d.data )
            else: # unsigned byte
                buf += struct.pack( '<B', d.data )

        return buf

    def encode_bool( self, cmd, data ):
        d = ng_data()
        d.byts = 0
        d.data = data
        return self.packetize( cmd, self.stringize( (d,) ) )

    def encode_idx_bool( self, cmd, idx, data ):
        i = ng_data()
        i.byts = 1
        i.data = data

        d = ng_data()
        d.byts = 0
        d.data = data

        return self.packetize( cmd, self.stringize( (i,d) ) )

    def encode_byte( self, cmd, data ):
        return self.encode_bytes( cmd, (data,) )

    def encode_bytes( self, cmd, data ):
        d = [ ]
        for i in data:
            ngd = ng_data()
            ngd.data = i
            d.append( ngd )
        return self.packetize( cmd, self.stringize( d ) )

    def set_pack_blocking( self, pack_id, block ):
        return self.encode_idx_bool( CMD_TCP_PACK_BLOCKING, pack_id, block )

    def get_gameserver_mode( self ):
        return self.packetize( CMD_TCP_CLIENT_GET_SERVER_MODE, '' )

    def get_all_pack_status( self ):
        return self.get_pack_status( 0xFF )

    def get_pack_status( self, pack_id ):
        return self.encode_bytes( CMD_TCP_GET_PACK_STATUS, (PACK_STATUS_REQUEST_TYPE_ALWAYS, pack_id) )



    ######################
    # Decoding functions #
    ######################


    # fmt should be a unpack format or True for bool
    def destringize( self, data, fmt = None ):
        if fmt is None:
            l = len(data)
            if( l == 4 ):
                fmt = '<i' # i = signed int, I = unsigned int
            elif( l == 2 ):
                fmt = '<H' # unsigned short int
            else:
                fmt = '<B' # unsigned byte
        elif( fmt is True ):
            fmt = '<?' # bool

        return struct.unpack( fmt, data )[0]

    def get_len( self ):
        if( len(self.buf) < 3 ):
            raise EOFError()

        return ord(self.buf[0]) + (ord(self.buf[1]) << 8)

    def want_bytes( self ):
        if( len(self.buf) < 3 ):
            return 3 - len(self.buf)

        want_len = self.get_len() + 3

        if( len(self.buf) < want_len ):
            return want_len - len(self.buf)

        return 0

    def have_pkt( self ):
        if( len(self.buf) < 3 ):
            return False

        want_len = self.get_len()

        # pack status packets are (num_packs * 5) + 1
        if( want_len > 1282 ):
            print 'Sanity Check Failed!  Discarding Packet Buffer!  Claimed packet size:', want_len
            self.buf = ''
            return False

        want_len += 3

        if( len(self.buf) < want_len ):
            return False

        return True

    def accumulate( self, newdata ):
        self.buf += newdata

    def decode( self ):
        if( not self.have_pkt() ):
            return None

        pkt = ng_packet()

        pkt.length = self.get_len()
        pkt.command = ord(self.buf[2])

        this_buf = self.buf[3:pkt.length+3]
        self.buf = self.buf[pkt.length+3:]

        if( pkt.length >= 8 ):
            pkt.event_type = self.destringize( this_buf[6:8] )

        if( pkt.command == CMD_TCP_PLAYER_EVENT ):
            if( pkt.length < 37 ):
                print 'Packet claims to be CMD_TCP_PLAYER_EVENT but is too short!'
                return self.decode( '' )

            pkt.is_player_event = True
            pkt.data = ng_player_event()

            pkt.data.event_idx = self.destringize( this_buf[:4] )
            pkt.data.player_id = self.destringize( this_buf[4] )
            pkt.data.player_team = self.destringize( this_buf[5] )
            pkt.data.event_type = self.destringize( this_buf[6:8] )
            pkt.data.score_applies = self.destringize( this_buf[8] )
            pkt.data.score = self.destringize( this_buf[9:13] )

            for i in range( 6 ):
                offset = 13 + (i * 4)
                pkt.data.rawdata[i] = self.destringize( this_buf[offset:offset+4] )

            # 0 - 27 are player tags
            # 28 - 29 are referee warn / term
            # 30 - 31 are base hit / destroy
            # 32 is player eliminated
            # 33 is tagged by base
            # 34 is tagged by mine
            # 35 is player fired / trigger
            # 36 is pack game state
            # 37 - 46 are player hit target
            # 47 is player reward
            # 48 is location beacon
            # 49 is tagged by clink gun

            if( pkt.data.event_type <= 27 ):
                pkt.data.player_tag = True
                pkt.data.event_data = ng_player_event_tag()

                if( pkt.data.event_type <= 13 ):
                    pkt.data.event_data.player_tagged_opponent = True
                    pkt.data.event_data.player_got_tagged = False
                else:
                    pkt.data.event_data.player_tagged_opponent = False
                    pkt.data.event_data.player_got_tagged = True

                pkt.data.event_data.opponent_id = pkt.data.rawdata[0]
                pkt.data.event_data.opponent_team = pkt.data.rawdata[1]
                pkt.data.event_data.weapon = pkt.data.rawdata[2]
                pkt.data.event_data.level = pkt.data.rawdata[3]
                pkt.data.event_data.tag_type = pkt.data.rawdata[4]
                pkt.data.event_data.health = pkt.data.rawdata[5]

            elif( pkt.data.event_type <= 29 ): # 28 and 29 are referee
                pass

            elif( pkt.data.event_type <= 31 ): # 30 and 31 are base hit/destroy
                pkt.data.base_hit = True
                pkt.data.event_data = ng_player_event_base()

                if( pkt.data.event_type == 31 ):
                    pkt.data.event_data.base_destroyed = True

                pkt.data.event_data.base_team = pkt.data.rawdata[0] & 0xFF

                base_id = (pkt.data.rawdata[0] >> 8) & 0xFF
                if( (base_id > 0) and (base_id < 255) ):
                    pkt.data.event_data.base_id = base_id - 1
                else:
                    pkt.data.event_data.base_id = None

                pkt.data.event_data.base_hit_time = ((pkt.data.rawdata[2] & 0xFFFF) / 13) - 1
                pkt.data.event_data.base_off_time = (((pkt.data.rawdata[2] >> 16) & 0xFFFF) / 13) - 1

            elif( pkt.data.event_type <= 34 ):
                # FIXME handle 32-34
                pass

            elif( pkt.data.event_type == 35 ): # trigger / fire
                pkt.data.player_fired = True

                pkt.data.event_data = ng_player_event_trigger()
                pkt.data.event_data.shots_fired = pkt.data.rawdata[0]
                pkt.data.event_data.power_remaining = pkt.data.rawdata[1]

            else:
                # FIXME handle 36+
                pass

        elif( pkt.command == CMD_TCP_PACK_BLOCKING ):
            pass

        elif( pkt.command == CMD_TCP_GET_PACK_STATUS ):
            pass

        elif( pkt.command == CMD_TCP_SET_PACK_NAME ):
            pass

        elif( pkt.command == CMD_TCP_CLIENT_REGISTER_TYPE ):
            pass

        elif( pkt.command == CMD_TCP_SERVER_MODE ):
            pkt.is_server_mode = True
            pkt.data = ng_server_mode()
            pkt.data.mode = self.destringize( this_buf[0] )
            pkt.data.time_remaining = self.destringize( this_buf[1:3] )
            pkt.data.mode_data = self.destringize( this_buf[3:] )

        elif( pkt.command == CMD_TCP_SERVER_PACK_STATUS ):
            pkt.is_pack_status = True
            pkt.data = ng_pack_status_pkt()
            pkt.data.num_packs = self.destringize( this_buf[0] )
            pkt.data.packs = { }

            #for i in range( pkt.data.num_packs ):
            #    pkt.data.packs.append( ng_pack_status( ) )

            this_buf = this_buf[1:]
            i = 0
            j = len( this_buf )

            while( i < j ):
                pack_id = self.destringize( this_buf[i] )
                pack_flags = self.destringize( this_buf[i+1] )
                pack_team  = self.destringize( this_buf[i+2] )
                pack_state = self.destringize( this_buf[i+3] )
                state_data = self.destringize( this_buf[i+4] )
                i += 5

                #if( pack_id >= pkt.data.num_packs ):
                #    print 'Pack ID out of range! pack:', pack_id, 'max pack:', pkt.data.num_packs
                #    continue

                pkt.data.packs[pack_id] = ng_pack_status( )
                pkt.data.packs[pack_id].flags = pack_flags
                pkt.data.packs[pack_id].team  = pack_team
                pkt.data.packs[pack_id].state = pack_state
                pkt.data.packs[pack_id].data  = state_data

        else:
            # FIXME
            pass

        return pkt
