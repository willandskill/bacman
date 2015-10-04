import os

from bacman import BacMan


class Postgres(BacMan):
    """ Take a snapshot of a Postgres DB. """

    filename_prefix = os.environ.get('BACMAN_PREFIX', 'pgdump')
    suffix = "bak"

    def get_command(self, path):
        command_string = "export PGPASSWORD={password}\npg_dump -Fc -U {user} -h {host} -p {port} {name} -f {path}"
        command = command_string.format(user=self.user,
                                        password=self.password,
                                        host=self.host,
                                        port=self.port,
                                        name=self.name,
                                        path=path)
        return command


if __name__ == "__main__":
    Postgres()