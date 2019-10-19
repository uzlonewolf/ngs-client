import sys, time, traceback, pprint

# get_var_name() is in ng.defs
from ng.defs import *

class gamedata:
    last_game_state = -1
    game_length = 0

def handle_packet( pkt, ourgamedata = None ):
    if( not pkt.is_server_mode ):
        print 'MT Got Packet:'
        pprint.pprint( dict(pkt), indent=4 )

    if( pkt.is_server_mode ):
        print 'current server mode is:', get_var_name( pkt.data.mode, 'SERVER_MODE_' ), '- game time remaining is', pkt.data.time_remaining, 'and extra data is', pkt.data.mode_data

        if( ourgamedata is None ):
            global gamedata
            ourgamedata = gamedata

        if( ourgamedata.last_game_state != pkt.data.mode ):
            print '!! Game Mode Changed !!'

        if( (pkt.data.mode == SERVER_MODE_IDLE) or (pkt.data.mode == SERVER_MODE_RUNNING) ):
            ourgamedata.game_length = 0
        elif( pkt.data.mode == SERVER_MODE_GAME_START ):
            if( (ourgamedata.last_game_state != SERVER_MODE_GAME_START) or (ourgamedata.game_length < 1) ):
                ourgamedata.game_length = pkt.data.time_remaining

            if( ourgamedata.game_length > 0 ):
                print 'game progress:', int((float(pkt.data.time_remaining) / ourgamedata.game_length) * 100), '%'

        ourgamedata.last_game_state = pkt.data.mode

    elif( pkt.is_pack_status ):
        print 'game server has', pkt.data.num_packs, 'packs installed'

        for pid in pkt.data.packs:
            pack = pkt.data.packs[pid]
            if( pack.flag( TCP_PACK_STATUS_FLAG_BLOCKED ) ):
                print 'pack', pid, 'is blocked'
            elif( not pack.flag( TCP_PACK_STATUS_FLAG_ONLINE ) ):
                print 'pack', pid, 'is ---offline---'
            elif( pack.state == 2 ): # can use PACK_STATE_CHARGING instead of 2 if ng_equ is included
                print 'pack', pid, 'is charging, charge current is', pack.data
            else:
                print 'pack', pid, 'is pack state', get_var_name( pack.state, 'PACK_STATE_' )

    elif( pkt.is_player_event ):
        print 'player event, score:', pkt.data.score, get_var_name( pkt.data.score_applies, 'PLAYER_EVENT_SCORE_APPLIES_' )

        if( pkt.data.player_fired ):
            print 'player', pkt.data.player_id, 'has fired, shots:', pkt.data.event_data.shots_fired, 'power remaining:', pkt.data.event_data.power_remaining

        elif( pkt.data.base_hit ):
            if( pkt.data.event_data.base_id is None ):
                print 'Base ID not in packet, please patch game script!'
                print >>sys.stderr, 'Base ID not in packet, please patch game script!'
            else:
                print 'Base ID:', pkt.data.event_data.base_id

            print 'Base Team:', pkt.data.event_data.base_team

            if( pkt.data.event_data.base_destroyed ):
                print 'Destroyed!'
            else:
                print 'Hit'

            if( (pkt.data.event_data.base_off_time == 0) and (pkt.data.event_data.base_hit_time == 0) ):
                print 'Base timers are not in packet, please patch game script!'
                print >>sys.stderr, 'Base timers are not in packet, please patch game script!'

        elif( pkt.data.player_tag ):
            if( pkt.data.event_data.player_got_tagged ):
                print 'player was hit by', pkt.data.event_data.opponent_id
            else:
                print 'player tagged opponent', pkt.data.event_data.opponent_id

