# coding: utf-8
import time

from pywss.ctx import Ctx


def logCost(ctx: Ctx):
    entry = time.time()
    ctx.next()
    ctx.log().withFields({"cost": f"{time.time() - entry}"}).info("exit")
