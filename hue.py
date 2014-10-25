from requests import get, put, post
from argparse import ArgumentParser
from json import dumps
from telnetlib import Telnet

URL = 'http://www.meethue.com/api/nupnp'
USER_NAME = 'retailinnovation'
ON_DICT = {"on": True, "bri": 255, "sat": 255, "hue": 0, "alert": "lselect"}


def authenticate(ip):
    url = 'http://{}/api/'.format(ip)
    payload = {
        "devicetype": "hue",
        "username": USER_NAME
    }
    response = post(url, dumps(payload))
    print response.text


def takeover_light(ip):
    t = Telnet()
    t.open(ip, 30000)
    t.write("[Link,Touchlink]")
    output = t.read_until("[Link,Touchlink,success", 10)
    print output
    t.close()


def add_light(ip):
    url = 'http://{}/api/{}/lights'.format(ip, USER_NAME)
    response = post(url)
    print response.text


def update_device(ip):
    url = "http://{}/api/{}/config".format(ip, USER_NAME)
    payload = {"portalservices": True}
    response = put(url, dumps(payload))
    print response.text

    print "reboot device then run again"

    payload = {"swupdate": {"updatestate": 3}}
    response = put(url, dumps(payload))
    print response.text


def get_bridge_list():
    response = get(URL)
    if response:
        return [bridge['internalipaddress'] for bridge in response.json()]


def toggle_group(on=False):
    put('{}/groups/0/action'.format(BRIDGE_URL), dumps({"on": on}))


def turn_light_on(light_id, light):
    if light and not light.get('state', {}).get('reachable'):
        print 'light {} does not appear to be reachable, skipping'.format(light_id)
        return False
    toggle_group()
    return put('{}/lights/{}/state'.format(BRIDGE_URL, light_id), dumps(ON_DICT))

if __name__ == '__main__':
    parser = ArgumentParser('Hue tool to identify a specific light.')
    parser.add_argument('--light_id', help='Light to turn on, minimum id 1', type=int)
    parser.add_argument('--ip', help='IP of hue bridge. Defaults to first bridge.')
    parser.add_argument('--user', default=USER_NAME, help='Authenticated user for hue.')
    parser.add_argument('--authenticate', default=False, help='Add user to hue bridge', action='store_true')
    parser.add_argument('--add_light', default=False, help='Add a light to the bridge', action='store_true')
    parser.add_argument('--update_device', default=False, help='Set device to go ahead and update', action='store_true')
    parser.add_argument('--takeover_light', default=False, help='Take over a light that belongs to another bridge',
                        action='store_true')
    parser.add_argument('--all_on', default=False, help='Turn all lights on', action='store_true')
    parser.add_argument('--all_off', default=False, help='Turn all lights off', action='store_true')
    args = parser.parse_args()

    if args.light_id is not None and args.light_id < 1:
        raise Exception('Hue light indices begin at 1.')

    if not args.ip:
        bridges = get_bridge_list()
        args.ip = bridges[0]

    if not args.ip:
        raise Exception('Could not find hue to connect to.')

    BRIDGE_URL = 'http://{}/api/{}'.format(args.ip, args.user)

    print 'using bridge at: {}'.format(args.ip)
    if args.authenticate:
        authenticate(args.ip)
    elif args.takeover_light:
        takeover_light(args.ip)
    elif args.add_light:
        add_light(args.ip)
    elif args.update_device:
        update_device(args.ip)
    elif args.all_on:
        toggle_group(on=True)
    elif args.all_off:
        toggle_group(on=False)
    elif args.light_id:
        resp = get('{}/lights/{}'.format(BRIDGE_URL, args.light_id))
        light = resp.json()
        turn_light_on(args.light_id, light)
    else:
        resp = get('{}/lights/'.format(BRIDGE_URL))
        status = resp.json()
        for light_id, light in status.iteritems():
            if turn_light_on(light_id, light):
                raw_input('light {} is on. Press enter for the next light.'.format(light_id))
