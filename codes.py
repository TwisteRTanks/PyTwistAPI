import enum


class Status(enum.IntEnum):

    unknown = -127
    permission_denied = -40
    ipacket = -3
    already_conn = -22
    ikey = -21
    iid = -20
    mconns_error = -1
    ok = 0
    