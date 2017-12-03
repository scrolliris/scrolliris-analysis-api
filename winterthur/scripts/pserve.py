import sys

from pyramid.scripts.pserve import PServeCommand

from winterthur.env import Env


def main(argv=sys.argv, quiet=False):
    Env.load_dotenv_vars()

    command = PServeCommand(argv, quiet=quiet)
    return command.run()


if __name__ == '__main__':
    sys.exit(main() or 0)
