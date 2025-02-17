"""
Calm Endpoint Sample of type Windows
"""
import json
from calm.dsl.runbooks import read_local_file
from calm.dsl.runbooks import basic_cred
from calm.dsl.builtins.models.metadata import Metadata
from calm.dsl.runbooks import CalmEndpoint as Endpoint
from calm.dsl.builtins.models.calm_ref import Ref
from tests.tunnel_endpoints.helper import get_vpc_tunnel_using_account, get_vpc_project

CRED_USERNAME = read_local_file(".tests/runbook_tests/username")
CRED_PASSWORD = read_local_file(".tests/runbook_tests/password")
VM_IP = read_local_file(".tests/runbook_tests/vm_ip")
DSL_CONFIG = json.loads(read_local_file(".tests/config.json"))

VPC_TUNNEL = get_vpc_tunnel_using_account(DSL_CONFIG)
VPC_PROJECT = get_vpc_project(DSL_CONFIG)

Cred = basic_cred(CRED_USERNAME, CRED_PASSWORD, name="endpoint_cred")
DslWindowsEndpoint = Endpoint.Windows.ip(
    [VM_IP], connection_protocol="HTTPS", cred=Cred, tunnel=Ref.Tunnel(name=VPC_TUNNEL)
)
