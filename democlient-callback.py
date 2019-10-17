import os, sys, time, traceback, pprint

from remap_stdout import RemapStdout

import ng.client
import handle_packet

if __name__ == "__main__":

    myname = os.path.basename(__file__)
    sys.stdout = RemapStdout(sys.stdout, 'stdout', myname+"-stdout-%s.log" % (time.strftime("%Y%m%d"), ) )
    sys.stderr = RemapStdout(sys.stderr, 'stderr', myname+"-stderr-%s.log" % (time.strftime("%Y%m%d"), ) )

    gamedata = handle_packet.gamedata()

    conn = ng.client.client( '192.168.2.3', 12100, handle_packet.handle_packet )

    try:
        conn.mainloop() # never exits!
    except (SystemExit, KeyboardInterrupt):
        print 'Main Thread Quitting!'
    except:
        traceback.print_exc()

    conn.stop()
