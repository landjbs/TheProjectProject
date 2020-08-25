from flask import request, url_for
from datetime import datetime
from collections import Counter
from operator import itemgetter


def tasks_to_daily_activity(tasks):
    current_time = datetime.utcnow()
    start_stamps = []
    end_stamps = []
    for task in tasks:
        start_stamps.append(round((current_time-task.post_stamp).days))
        # start_stamps.append((current_time-task.post_stamp).days)
        if task.complete:
            end_stamps.append(round(((current_time-task.complete_stamp).days)))
            # end_stamps.append((current_time-task.complete_stamp).days)
    start_activity = Counter(start_stamps)
    end_activity = Counter(end_stamps)
    earliest = max(start_activity)+1
    for i in range(earliest):
        if i not in start_activity:
            start_activity.update({i:0})
        if i not in end_activity:
            end_activity.update({i:0})
    start_activity = [x[1] for x in sorted(start_activity.items(), key=itemgetter(0), reverse=True)]
    end_activity = [x[1] for x in sorted(end_activity.items(), key=itemgetter(0), reverse=True)]
    # for i in range(start_activity):
    return (start_activity, end_activity, earliest)


def url_for_other_page(**kwargs):
    ''' Generates target url with pjax and url_for_args '''
    url_for_args = request.arg.copy()
    if 'pjax' in url_for_args:
        url_for_args.pop('_pjax')
    for k, v in kwargs.items():
        url_for_args[key] = value
    return url_for(request.endpoint, **url_for_args)


def partition_query(l, override_partition=False):
    if not override_partition:
        n = 3 if not request.MOBILE else 1
    else:
        n = override_partition
    try:
        c = l.count()
    except:
        c = len(l)
    return [l[i:i+n] for i in range(0, c, n)]
    # uncomment if should be generator
    # for i in range(0, c, n):
        # yield l[i:i+n]


def filter_string(s):
    '''
    Cleans and filters out strings with whitespace. Returns None if string
    has no substance.
    '''
    s = s.strip()
    return (s if s!='' else None)
