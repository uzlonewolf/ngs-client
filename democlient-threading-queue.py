import os, sys, time, traceback, pprint, Queue, threading

from remap_stdout import RemapStdout

# get_var_name() is in ng.defs
from ng.defs import *
import ng.client

def wait_for_exit( thread, timeo = 7 ):
    thread.join( timeo )

    if( not thread.isAlive() ):
        return True

    return False


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


    q = Queue.Queue()

    conn = ng.client.client( '192.168.2.3', 12100, q )

    thread = threading.Thread(target=conn.mainloop)
    thread.setDaemon(True)
    thread.start()

    run = True

    while run:
        try:
            pkt = q.get( timeout=1 ) # Allow check for Ctrl-C every second
            handle_packet( pkt )
            q.task_done()
        except (SystemExit, KeyboardInterrupt):
            print 'Main Thread Quitting!'
            run = False
        except Queue.Empty:
            pass
        except:
            traceback.print_exc()
            run = False

    conn.stop()

    # clear the queue so we can join()
    try:
        while True:
            pkt = q.get_nowait()
            handle_packet( pkt )
            q.task_done()
    except:
        pass

    try:
        q.task_done()
    except:
        pass

    q.join()

    if( not wait_for_exit( thread ) ):
        print 'GS Connection did not close!'
