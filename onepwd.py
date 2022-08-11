from typing import Optional
import keyring.backend
import subprocess as sp
import json


class OnePwdKeyring(keyring.backend.KeyringBackend):
    def set_password(self, servicename: str, username: str, password: str) -> None:
        raise NotImplemented

    def get_password(self, service: str, username: str) -> Optional[str]:
        # treat "service" as item name
        # username is ignored
        # returns json serialized username & password
        retries = 0
        while True:
            if retries >= 5:
                raise RuntimeError("Retried too many times with op. Exiting.")
            try:
                completed_process = sp.run(["op", "item", "get", service, "--fields", "label=username,label=password", "--format", "json"], stdout=sp.PIPE, stderr=sp.PIPE, timeout=30)
            except sp.TimeoutExpired:
                print(f"Process timed out (30 seconds), retrying...")
                retries += 1
                continue
            returncode = completed_process.returncode
            if returncode != 0:
                print(f"Process returned {returncode} != 0, retrying...")
                print(f"Error details: {completed_process.stderr}")
                retries += 1
            else:
                output = completed_process.stdout
                output = json.loads(output)
                username = ""
                password = ""
                for item in output:
                    if item['label'] == 'username':
                        username = item["value"]
                    elif item['label'] == 'password':
                        password = item["value"]
                return json.dumps({
                    "username": username,
                    "password": password
                })

    def delete_password(self, service: str, username: str) -> None:
        raise NotImplemented