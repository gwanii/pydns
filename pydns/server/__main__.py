import argparse, logging, asyncio
from . import DNSServer
from ..resolver import AsyncProxyResolver
from ..logger import logger

def main():
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(description='DNS server by Gerald.')
    parser.add_argument('-b', '--bind', default=':',
            help='the address for the server to bind')
    parser.add_argument('--hosts', help='the path of a hosts file')
    parser.add_argument('-P', '--proxy', nargs='+',
            default=AsyncProxyResolver.DEFAULT_NAMESERVERS,
            help='the proxy DNS servers')
    parser.add_argument('-p', '--protocol', choices=['udp', 'tcp'], default='udp',
            help='whether to use TCP protocol as default to query remote servers')
    args = parser.parse_args()

    host, _, port = args.bind.rpartition(':')
    if not host: host = '0.0.0.0'
    if port:
        port = int(port)
    else:
        port = 53

    server = DNSServer(host, port, hosts = args.hosts, resolve_protocol = args.protocol, proxies = args.proxy)
    logger.info('DNS server v2 - by Gerald')
    loop = asyncio.get_event_loop()
    tcpserver, udptransport = loop.run_until_complete(server.start_server())
    if tcpserver is not None:
        logger.info('Serving on %s, port %d, TCP', *(tcpserver.sockets[0].getsockname()[:2]))
    if udptransport is not None:
        sock = udptransport.get_extra_info('socket')
        logger.info('Serving on %s, port %d, UDP', *(sock.getsockname()[:2]))
    loop.run_forever()

main()
