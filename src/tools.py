# -*- coding: utf-8 -*-
def pretty_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h == 0:
        if m != 0 and s == 0:
            return "{} ".format(m) + min_label(m)
        elif s != 0 and m == 0:
            return "{} ".format(s) + sec_label(m)
        else:
            return "%02d:%02d" % (m, s)
    elif h == 0 and m == 0 and s > 0:
        return "%02d min" % m
    else:
        return "%d:%02d:%02d" % (h, m, s)


def min_label(minutes):
    return {1: 'minuta', 2: 'minuty', 3: 'minuty', 4: 'minuty'}.get(minutes, 'minut')


def sec_label(seconds):
    return {1: 'sekunda', 2: 'sekundy', 3: 'sekundy', 4: 'sekundy'}.get(seconds, 'sekund')
