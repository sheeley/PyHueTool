from pyhue import Bridge
from requests import get
from argparse import ArgumentParser

URL = 'http://www.meethue.com/api/nupnp'
USER_NAME = 'retailinnovation'


def get_bridge_list():
    response = get(URL)
    if response:
        return [bridge['internalipaddress'] for bridge in response.json()]

if __name__ == '__main__':
    parser = ArgumentParser('Hue tool to identify a specific light.')
    parser.add_argument('light_id', help='Light to turn on, minimum id 1', type=int)
    parser.add_argument('--ip', dest='ip', help='IP of hue bridge. Defaults to first bridge.')
    parser.add_argument('--user', dest='user_name', default=USER_NAME, help='Authenticated user for hue.')
    args, _ = parser.parse_known_args()

    if args.light_id < 1:
        raise Exception('Hue light indices begin at 1.')

    if not args.ip:
        bridges = get_bridge_list()
        args.ip = bridges[0]

    if not args.ip:
        raise Exception('Could not find hue to connect to.')

    bridge = Bridge(args.ip, args.user_name)

    print 'using bridge at: {}'.format(args.ip)

    print 'turning all lights off'
    bridge.groups[0].on = False

    print 'setting light {} on'.format(args.light_id)
    bridge.lights[args.light_id].on = True
