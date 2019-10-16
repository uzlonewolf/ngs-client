import os, sys, time, traceback, pprint

from remap_stdout import RemapStdout

# get_var_name() is in ng.defs
from ng.defs import *
import ng.client

def handle_packet( pkt ):
    print 'MT Got Packet:'
    pprint.pprint( dict(pkt), indent=4 )

    if( pkt.is_server_mode ):
        print 'current server mode is:', get_var_name( pkt.data.mode, 'SERVER_MODE_' )
        print 'game time remaining is:', pkt.data.time_remaining
        print 'extra data is:', pkt.data.mode_data
    elif( pkt.is_pack_status ):
        print 'FIXME! pack status'
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

if __name__ == "__main__":

    myname = os.path.basename(__file__)
    sys.stdout = RemapStdout(sys.stdout, 'stdout', myname+"-stdout-%s.log" % (time.strftime("%Y%m%d"), ) )
    sys.stderr = RemapStdout(sys.stderr, 'stderr', myname+"-stderr-%s.log" % (time.strftime("%Y%m%d"), ) )

    conn = ng.client.client( '192.168.2.3', 12100, handle_packet )

    try:
        conn.mainloop() # never exits!
    except (SystemExit, KeyboardInterrupt):
        print 'Main Thread Quitting!'
    except:
        traceback.print_exc()

    conn.stop()
