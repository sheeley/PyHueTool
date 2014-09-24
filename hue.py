from requests import get, put
from argparse import ArgumentParser
from json import dumps

URL = 'http://www.meethue.com/api/nupnp'
USER_NAME = 'retailinnovation'
ON_DICT = {"on": True, "bri": 255, "sat": 255, "hue": 0}
OFF_DICT = {"on": False}


def get_bridge_list():
    response = get(URL)
    if response:
        return [bridge['internalipaddress'] for bridge in response.json()]


def turn_group_off():
    put('{}/groups/0/action'.format(BRIDGE_URL), dumps(OFF_DICT))


def turn_light_on(light_id, light):
    if light and not light.get('state', {}).get('reachable'):
        print 'light {} does not appear to be reachable, skipping'.format(light_id)
        return False
    turn_group_off()
    return put('{}/lights/{}/state'.format(BRIDGE_URL, light_id), dumps(ON_DICT))

if __name__ == '__main__':
    parser = ArgumentParser('Hue tool to identify a specific light.')
    parser.add_argument('--light_id', help='Light to turn on, minimum id 1', type=int)
    parser.add_argument('--ip', help='IP of hue bridge. Defaults to first bridge.')
    parser.add_argument('--user', default=USER_NAME, help='Authenticated user for hue.')
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

    if args.light_id:
        resp = get('{}/lights/{}'.format(BRIDGE_URL, args.light_id))
        light = resp.json()
        turn_light_on(args.light_id, light)
    else:
        resp = get('{}/lights/'.format(BRIDGE_URL))
        status = resp.json()
        for light_id, light in status.iteritems():
            if turn_light_on(light_id, light):
                raw_input('light {} is on. Press enter for the next light.'.format(light_id))
