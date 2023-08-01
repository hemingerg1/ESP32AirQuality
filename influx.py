import urequests
import uasyncio
import gc
import aqUtils
import secrets

log = aqUtils.get_logger()

async def influxSend(data):
    url = secrets.INFLUX_URL
    header = {'Authorization': secrets.INFLUX_TOKEN}

    r = urequests.post(url=url, headers=header, data=data)

    if 200 <= r.status_code < 300:
        log.warn(f'Influx post unsuccessful. Error: "{r.json()["code"]}"')

    r.close()
    gc.collect()
    return