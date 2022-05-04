"""
Print all managers of the groups with access to a provided vault

Classes:

    Group

Functions:

    get_vault_groups(string) -> list
"""

import sys
import subprocess
import json
import argparse


class Group:
    """
    A class to respresent a 1Password Group

    ...

    Attributes
    ----------
    group_name : str
        name of the 1Password group
    managers : list
        list of managers for the 1Password group

    Methods
    -------
    get_managers():
        Collects the list of managers and sets the managers attribute

    print_managers():
        Prints the name of the group followed by the list of managers names and emails

    Parameters
    ----------
    group_name : str
        name of the 1Password group
    """

    def __init__(self, group_name):
        self.group_name = group_name
        self.managers = []

    def get_managers(self, account):
        """Appends the name and email addresses of the groups managers to the managers variable"""
        cmd = ["op", "--format", "json", "group", "user", "list", self.group_name]
        if account:
            cmd = [
                "op",
                "--format",
                "json",
                "--account",
                account,
                "group",
                "user",
                "list",
                self.group_name,
            ]
        data = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if data.stderr:
            print(data.stderr, end="")
            sys.exit(1)
        data = json.loads(data.stdout)
        if data == "null":
            return
        for user in data:
            role = user.get("role")
            name = user.get("name")
            email = user.get("email")
            state = user.get("state")
            if role == "MANAGER" and state == "ACTIVE":
                self.managers.append([name, email])

    def print_managers(self):
        """Prints the name of the group followed by the name and email of each manager"""
        print(self.group_name)
        if not self.managers:
            print("No managers for this group")
        for manager in self.managers:
            print(f"{manager[0]}, {manager[1]}")
        print("")

    def print_for_csv(self):
        """Prints the group, name, and email address of each manager to be piped to a csv"""
        if not self.managers:
            pass
        else:
            for manager in self.managers:
                print(f"{self.group_name},{manager[0]},{manager[1]}")


def get_vault_groups(vault):
    """
    Collects and returns all of the groups that have access to the provided group

    Parameters
    ----------
    vault : str
        The name of the 1Password vault

    Returns
    -------
    list
    A list of all of the groups that have access to the requested vault
    """
    vault_groups = []
    cmd = ["op", "--format", "json", "vault", "group", "list", vault]
    data = subprocess.run(cmd, capture_output=True, text=True, check=False)
    data = json.loads(data.stdout)
    for group in data:
        name = group.get("name")
        vault_groups.append(name)
    return vault_groups


def main():
    """Gets and prints all of the managers of groups with access to the provided vault"""
    parser = argparse.ArgumentParser()
    parser.add_argument("vault", type=str, help="Name of vault to get managers from")
    parser.add_argument(
        "-a",
        "--account",
        type=str,
        help="Shortname of your 1Password account",
        dest="account",
    )
    parser.add_argument(
        "-c",
        "--csv",
        action="store_true",
        help="Set this flag to print output in csv format.",
        dest="csv",
    )

    args = parser.parse_args()

    groups = []
    vault_groups = get_vault_groups(args.vault)
    for vault_group in vault_groups:
        groups.append(Group(vault_group))
    for group in groups:
        group.get_managers(args.account)
    if args.csv:
        print("group,name,email")
        for group in groups:
            group.print_for_csv()
    else:
        for group in groups:
            group.print_managers()


if __name__ == "__main__":

    main()
