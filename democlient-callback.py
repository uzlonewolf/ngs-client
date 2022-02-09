import os, sys, time, traceback, pprint

from remap_stdout import RemapStdout

import ng.client
import handle_packet

def opened( conn ):
    print( 'opened' )
    #conn.send( conn.ng_pkt.restore_teams() ) # no data, uses teams stored in Setup.ini
    #conn.send( conn.ng_pkt.set_pack_team( 0, 6 ) )
    #conn.send( conn.ng_pkt.set_pack_name( 0, 'Astrooo' ) )

def poll( conn ):
    print( 'sending poll' )

if __name__ == "__main__":

    myname = os.path.basename(__file__)
    sys.stdout = RemapStdout(sys.stdout, 'stdout', myname+"-stdout-%s.log" % (time.strftime("%Y%m%d"), ) )
    sys.stderr = RemapStdout(sys.stderr, 'stderr', myname+"-stderr-%s.log" % (time.strftime("%Y%m%d"), ) )

    handler = handle_packet.handle_packet()

    conn = ng.client.client( '192.168.2.3', 12100 )
    conn.on_message = handler.handle_packet
    conn.on_connect = opened
    conn.on_poll = poll
    #conn.on_close =
    conn.print_hex = True
    conn.want_pack_state()

    try:
        conn.run_forever() # never exits!
    except (SystemExit, KeyboardInterrupt):
        print 'Main Thread Quitting!'
    except:
        traceback.print_exc()

    conn.stop()
