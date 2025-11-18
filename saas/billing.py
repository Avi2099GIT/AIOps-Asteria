# Billing stub - usage metering placeholder
def record_usage(tenant_id, metric, value):
    print(f"[BILLING] {tenant_id} - {metric} = {value}")
    return True
