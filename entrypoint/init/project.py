# coding: utf-8
import cc
import loggus


class ProjectCommand(cc.Command):
    class flags:
        name = cc.FlagStr(flags=["-n", "--name"], description="project name", require=True)

    def run(self, *args, **flags):
        loggus.info(f"init project: {self.flags.name.value()}")
