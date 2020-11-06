"""
TerminalCommand class is used to run commands from python as if we are in a shell/cmd
"""
import subprocess as p

__all__ = ['TerminalCommand']


class TerminalCommand:
    def __init__(self, cmd, cwd=None, env=None):
        """
        Creates a new command container.
        Note that this immediately executes the command synchronously and writes the
        return values to the corresponding members.

        Attributes
        ----------
        cmd : The command to execute.
        cwd : The working directory to run the command in.
        env : The environment the command is run in.
        """
        process = p.Popen(cmd, stdout=p.PIPE, stderr=p.PIPE, shell=True, cwd=cwd, env=env)
        stdout, stderr = process.communicate()

        self.stdout = stdout.decode('utf8')
        self.stderr = stderr.decode('utf8')

        self.return_code = process.returncode
        process.kill()

    def is_success(self):
        return self.return_code == 0

    def is_failure(self):
        return self.return_code != 0

    def get_split_output_strings(self):
        lines = self.stdout.splitlines()
        words = []
        [words.append(word) for line in lines for word in line.split()]
        return words


if __name__ == "__main__":
    pass
