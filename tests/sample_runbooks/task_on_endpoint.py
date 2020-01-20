"""
Calm Runbook Sample for task running on an endpoint
"""

from calm.dsl.builtins import read_local_file
from calm.dsl.builtins import runbook, RunbookService
from calm.dsl.builtins import basic_cred, CalmTask
from calm.dsl.builtins import CalmEndpoint, ref

CRED_USERNAME = read_local_file(".tests/runbook_tests/username")
CRED_PASSWORD = read_local_file(".tests/runbook_tests/password")
VM_IP = read_local_file(".tests/runbook_tests/vm_ip")

Cred = basic_cred(CRED_USERNAME, CRED_PASSWORD, name="endpoint_cred")
endpoint = CalmEndpoint.Linux.ip([VM_IP], cred=Cred)

script = """
         echo "Welcome to task 1"
         hostname
         ip r s
         date
 """


class DslTaskOnEndpoint(RunbookService):
    "Runbook Service example"

    @runbook
    def main_runbook():
        CalmTask.Exec.ssh(name="Task1", script=script, target=ref(endpoint))

    endpoints = [endpoint]
    credentials = []


def main():
    print(DslTaskOnEndpoint.json_dumps(pprint=True))


if __name__ == "__main__":
    main()