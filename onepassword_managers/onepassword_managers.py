"""
Print all managers of the groups with access to a provided vault

Classes:

    Group

Functions:

    get_vault_groups(string) -> list
"""

import subprocess
import json
import argparse

from classes.classes import Group  # pylint: disable=import-error


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
        group.set_members(args.account)
        group.set_managers()
    if args.csv:
        print("group,name,email")
        for group in groups:
            group.print_for_csv()
    else:
        for group in groups:
            group.print_managers()


if __name__ == "__main__":

    main()
