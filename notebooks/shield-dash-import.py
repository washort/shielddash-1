import datetime
from operator import itemgetter

import ujson
from moztelemetry import get_pings


PING_NAME = 'x-shield-studies'
HEARTBEAT_NAME = 'x-shield-study-performance-1'
STUDY_NAME = 'screen Performance X1'
STUDY_START = '20160325'
TODAY = datetime.date.today().strftime('%Y%m%d')


def getShieldProps(p):
    out = {
        'client_id': p.get('clientId'),
        'channel': p['application']['channel'],
        'creation_date': datetime.datetime.utcfromtimestamp(
            long(p['meta']['creationTimestamp']) // 1e9),
        'doc_type': p['meta']['docType']
    }
    for k in ['firstrun', 'msg', 'name', 'variation']:
        if k == 'firstrun':
            out[k] = datetime.datetime.utcfromtimestamp(
                int(p['payload'][k]) // 1e3)
        else:
            out[k] = p['payload'][k]
    return out


kwargs = {
    'doc_type': 'OTHER',
    'submission_date': (STUDY_START, TODAY),
    'app': 'Firefox',
}


pings = get_pings(sc, channel='release', **kwargs).union(
    get_pings(sc, channel='aurora', **kwargs)).union(
        get_pings(sc, channel='beta', **kwargs)).union(
            get_pings(sc, channel='nightly', **kwargs))
pings = pings.filter(lambda p: p['meta']['docType'] == PING_NAME)
pings = pings.filter(lambda p: p['payload']['name'] == STUDY_NAME)
pings = pings.map(getShieldProps).filter(itemgetter('client_id'))


summaryProto = {
    'channel': None,
    'completed': False,
    'ineligible': False,
    'installed': False,
    'left_study': False,
    'seen1': False,
    'seen2': False,
    'seen3': False,
    'seen7': False,
    'variation': None,
}


def aggUV(agg, item):
    for k in ('channel', 'variation'):
        agg[k] = item[k]

    days = (item['creation_date'] - item['firstrun']).days
    if days in (1, 2, 3, 7):
        agg['seen%d' % days] = True

    msg = item['msg']
    if msg == 'user-ended-study':
        agg['left_study'] = True
    elif msg == 'install':
        agg['installed'] = True
    elif msg == 'end-of-study':
        agg['completed'] = True
    elif msg == 'ineligible':
        agg['ineligible'] = True

    return agg


def aggUU(agg1, agg2):
    for k, v in agg2.iteritems():
        if v:
            agg1[k] = v
    return agg1


states = (pings.keyBy(itemgetter('client_id'))
               .aggregateByKey(summaryProto, aggUV, aggUU)).values()

ujson.dump(states.collect(), open('output/shield-dash.json', 'w'))
