def trigger_incident(summary, details):
    print('[PAGERDUTY] incident triggered', summary)
    return {'status':'triggered'}
