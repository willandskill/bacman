import os

from bacman import BacMan


class MySQL(BacMan):
    """Take a snapshot of a MySQL DB."""

    filename_prefix = os.environ.get('BACMAN_PREFIX', 'mysqldump')

    def get_command(self, path):
        command_string = "mysqldump -u {user} -p{password} -h {host} {name} > {path}"
        command = command_string.format(user=self.user,
                                        password=self.password,
                                        host=self.host,
                                        name=self.name,
                                        path=path)
        return command


if __name__ == "__main__":
    MySQL()