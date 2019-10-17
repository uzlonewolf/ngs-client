import os, sys, time, traceback, pprint, Queue, threading

from remap_stdout import RemapStdout

import ng.client
import handle_packet

def wait_for_exit( thread, timeo = 7 ):
    thread.join( timeo )

    if( not thread.isAlive() ):
        return True

    return False

if __name__ == "__main__":

    myname = os.path.basename(__file__)
    sys.stdout = RemapStdout(sys.stdout, 'stdout', myname+"-stdout-%s.log" % (time.strftime("%Y%m%d"), ) )
    sys.stderr = RemapStdout(sys.stderr, 'stderr', myname+"-stderr-%s.log" % (time.strftime("%Y%m%d"), ) )


    q = Queue.Queue()
    gamedata = handle_packet.gamedata()

    conn = ng.client.client( '192.168.2.3', 12100, q )

    thread = threading.Thread(target=conn.run_forever)
    thread.setDaemon(True)
    thread.start()

    run = True

    while run:
        try:
            pkt = q.get( timeout=1 ) # Allow check for Ctrl-C every second
            handle_packet.handle_packet( pkt, gamedata )
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
