# -*- coding: utf-8 -*-

import sys
import argparse
import getpass
import os
from launcher.login import Login
from launcher.urlchecker import UrlChecker
from launcher.makinator import do_openstack_login



def _parse_arguments():
    parser = argparse.ArgumentParser(description="Launch virtual machines to OpenStack")

    parser.add_argument('-u', '--user', action='store', dest='username', 
                        help='The username for login. Defaults to env[LAUNCHER_USER].')
    parser.add_argument('-p', '--password', action='store_true', dest='password',
                        help='The password will be prompted after run the program. Defaults to env[LAUNCHER_PASSWORD].')
    parser.add_argument('--url', action='store', dest='url',
                        help='The authentication url of the form http://hostname:5000/v2.0 . Defaults to env[LAUNCHER_URL].')
    parser.add_argument('--tenant', action='store', dest='tenant',
                        help='The tenant name. Defaults to env[LAUNCHER_TENANT].')
    parser.add_argument('--instances', action='store', dest='instances', 
                        type=int, default=1, 
                        help='Number of instances to launch. Default: 1')

    image_group = parser.add_argument_group('Image options')
    igexclusive = image_group.add_mutually_exclusive_group()
    igexclusive.add_argument('--image', action='store', dest='image', 
                       help="Image name to launch")
    igexclusive.add_argument('--ilist', action='store_true', 
                             help='List all images availables')

    flavour_group = parser.add_argument_group('Flavour options')
    fgexclusive = flavour_group.add_mutually_exclusive_group()
    fgexclusive.add_argument('--flavour', help='Flavour to use')
    fgexclusive.add_argument('--flist', action='store_true', 
                             help='List all available flavours')
    
    security_group = parser.add_argument_group('Security groups options')
    sgexclusive = security_group.add_mutually_exclusive_group()
    sgexclusive.add_argument('--secgroup', help='Security group to use')
    sgexclusive.add_argument('--secgrouplist', help='List all available security groups')

    keypair_group = parser.add_argument_group('Keypair options')
    kgexclusive = keypair_group.add_mutually_exclusive_group()
    kgexclusive.add_argument('--keypair', help='Keypair to use')
    kgexclusive.add_argument('--keypairlist', help='List all available keypairs')
    return parser.parse_args()


def is_valid_url(nurl):
    url_ = UrlChecker(nurl)
    proto = url_.check_url_protocol()
    port = url_.check_url_port()
    if not proto or not port:
        return False
    return True

def set_credentials(param):
    try:
        os.environ['LAUNCHER_' + param.upper()]
    except KeyError, e:
        print >> sys.stderr, 'Error. {0} not provided.'.format(e.message)
        sys.exit(3) 

def main():
    arguments = _parse_arguments()
    if not arguments.username:
        set_credentials('username')
    elif not arguments.password:
        set_credentials('password')
    elif not arguments.url:
        set_credentials('url')
    elif not arguments.tenant:
        set_credentials('tenant')        
    pwd = getpass.getpass().strip()
    if not pwd:
        print >> sys.stderr, 'Error: No password provided'
        return 1
    url = arguments.url
    if not is_valid_url(url):
        print >> sys.stderr, "Url not valid"
        return 2
    tenant = arguments.tenant
    logininfo = Login(user, pwd, url, tenant)
    return 0
    nova = do_openstack_login(logininfo)
    image = get_image_name(nova, "CirrOS 0.3.1")
    flavour = get_flavour_list(nova, "m1.tiny")
    secgroup = get_security_group(nova)
    keypair = get_keypairs(nova)
    if not any([image, flavour]):
        print >> sys.stderr, "Not enough parameters"
        sys.exit(1)
    imgs = launch_virtual_machines(nova, "test", image, flavour, 
                                   secgroup=secgroup, kpair=keypair)
    return 0


if __name__ == '__main__':
    sys.exit(main())