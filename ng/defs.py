
try:
    from ng_equ import *
except:
    print 'ng_equ not found, gamescript defines not available!'

GAME_PROFILE   = 0
GAME_PLAYING   = 1
GAME_ENDING    = 2
GAME_UNDEFINED = 3

SERVER_MODE_STARTUP             = 0
SERVER_MODE_IDLE                = 1
SERVER_MODE_RUNNING             = 2
SERVER_MODE_GAME_START_REQUEST  = 3
SERVER_MODE_GAME_START          = 4
SERVER_MODE_GAME_ABORT_REQUEST  = 5
SERVER_MODE_GAME_ABORT          = 6
SERVER_MODE_GAME_FINISH_REQUEST = 7
SERVER_MODE_GAME_FINISH         = 8
SERVER_MODE_HISTORY_COMPILE     = 9
SERVER_MODE_EMERGENCY_REQUEST   = 10
SERVER_MODE_EMERGENCY           = 11
SERVER_MODE_GAME_CHANGE_REQUEST = 12
SERVER_MODE_SHUTDOWN_REQUEST    = 13
SERVER_MODE_SHUTDOWN            = 14

CMD_TCP_CLIENT_GET_SERVER_MODE     = 0
#CMD_TCP_CLIENT_GET_SERVER_MODE_LENGTH 0
CMD_TCP_CLIENT_GET_PACK_STATUS_ALL = 1
CMD_TCP_CLIENT_MODE_REQUEST        = 2
#CMD_TCP_CLIENT_MODE_REQUEST_LENGTH 1
CMD_TCP_SET_CLIENT_AUTO_SEND       = 3
#CMD_TCP_SET_CLIENT_AUTO_SEND_LENGTH 1
CMD_TCP_CLIENT_GET_GAME_EVENT      = 4
CMD_TCP_PLAYER_EVENT               = 5
CMD_TCP_PACK_BLOCKING              = 6
#CMD_TCP_PACK_BLOCKING_LENGTH 2
CMD_TCP_GET_PACK_STATUS            = 7
CMD_TCP_UNKNOWN_CMD_8              = 8
CMD_TCP_SET_PACK_NAME              = 9 # i.e. 0900 09 00 417374726f6f6f20 -> Pack 0 to "Astrooo "
CMD_TCP_CLIENT_REGISTER_TYPE       = 11
#CMD_TCP_CLIENT_REGISTER_TYPE_LENGTH 1

CMD_TCP_SERVER_MODE                = 128
CMD_TCP_SERVER_PACK_STATUS         = 129

CMD_LW_ARENA_CLEAR                 = 250

AUTO_SEND_SERVER_MODE = 0
AUTO_SEND_GAME_EVENTS = 4

MODE_REQUEST_TYPE_GAME_START  = 0
MODE_REQUEST_TYPE_GAME_ABORT  = 1
MODE_REQUEST_TYPE_GAME_FINISH = 2
MODE_REQUEST_TYPE_GAME_CHANGE = 3

CLIENT_REGISTER_TYPE_SCOREBOARD = 2

PACK_BLOCKING_UNBLOCK = 0
PACK_BLOCKING_BLOCK   = 1

PACK_STATUS_REQUEST_TYPE_ALWAYS    = 0
PACK_STATUS_REQUEST_TYPE_ON_CHANGE = 1

TCP_PACK_STATUS_FLAG_BLOCKED          =  1
TCP_PACK_STATUS_FLAG_ONLINE           =  2
TCP_PACK_STATUS_FLAG_ALLOCATED        =  4
TCP_PACK_STATUS_FLAG_PLAYING          =  8
TCP_PACK_STATUS_FLAG_MEMBER_LOGGED_ON = 16

PATTERN_NONE         = 0
PATTERN_GAME_OVER    = 1
PATTERN_CRAWLER      = 2
PATTERN_BASE_HIT     = 3
PATTERN_BASE_DESTROY = 4
PATTERN_GAME_START   = 5
PATTERN_ARENA_CLEAR  = 6
#PATTERN_             = 0                                                                                                                                          


PATTERN_CMD_DATA           = 0
PATTERN_CMD_WAIT           = 1
PATTERN_CMD_LOOP_TIME      = 2
PATTERN_CMD_LOOP_COUNT     = 3
PATTERN_CMD_SECTION        = 4
PATTERN_CMD_FINISHED       = 5
PATTERN_CMD_LAYER          = 6
PATTERN_CMD_FINISH_SECTION = 7

CLIENT_COMMAND_NULL  = 0
CLIENT_COMMAND_DATA  = 1
CLIENT_COMMAND_CLEAR = 2


ACTION_DIE   = 1
ACTION_TIMER = 2


def get_var_name( val, prefix = None ):
    #for key, value in vars(ng_equ).iteritems():
    for key, value in globals().iteritems():
        #print 'checking', key, prefix, value, val
        if( prefix is None ):
            if( val == value ):
                return key

        elif( (val == value) and (key[:len(prefix)] == prefix) ):
            return key

    # not found!
    #print 'var name not found for prefix', prefix, 'val', val
    return val


