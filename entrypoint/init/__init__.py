# coding: utf-8
import cc

from .project import ProjectCommand


class InitCommand(cc.Command):

    def __init__(self):
        super().__init__()
        self.add(ProjectCommand())
