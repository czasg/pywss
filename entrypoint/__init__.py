# coding: utf-8
import cc
import entrypoint.init
import entrypoint.server


class PywssCommand(cc.Command):

    def usages(self) -> str:
        return "pywss [COMMAND] [OPTIONS]"

    def descriptions(self) -> str:
        return """
        Pywss is a lightweight Python Web framework built on Python3.6+ features.
        Different from the mainstream frameworks such as Flask and Django,
        Pywss is also more similar to frameworks such as Gin, Iris, etc.
        So Pywss is a project well worth exploring for developers familiar with these frameworks.
        More detail please see `https://github.com/czasg/pywss`.
        """


def main():
    cmd = PywssCommand()
    cmd.add(
        entrypoint.init.InitCommand(),
        entrypoint.server.ServerCommand(),
    )
    cc.Execute(cmd)


if __name__ == '__main__':
    main()
