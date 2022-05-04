import sys
import subprocess
import json


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
        try:
            for user in data:
                role = user.get("role")
                name = user.get("name")
                email = user.get("email")
                state = user.get("state")
                if role == "MANAGER" and state == "ACTIVE":
                    self.managers.append([name, email])
        except TypeError:
            return

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
