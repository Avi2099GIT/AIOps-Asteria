import os, json, asyncio
from typing import Dict, Any
from api.app.core.config import settings


KAFKA_BOOTSTRAP = os.environ.get('KAFKA_BOOTSTRAP', settings.kafka_bootstrap)
print("BOOTSTRAP SERVERS =", KAFKA_BOOTSTRAP)
TOPIC = os.environ.get('ASTERIA_EVENTS_TOPIC', settings.events_topic)

# Try confluent_kafka, if not available fallback to local file (dev)
try:
    from confluent_kafka import Producer
    _producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})
except Exception as e:
    _producer = None

async def produce_event(event: Dict[str, Any]):
    data = json.dumps(event)
    if _producer:
        def delivery(err, msg):
            if err:
                print('Delivery failed:', err)
        _producer.produce(TOPIC, data.encode('utf-8'), callback=delivery)
        _producer.flush(0)
    else:
        # fallback write to file
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: open('/tmp/asteria_events.log','a').write(data+'\n'))
