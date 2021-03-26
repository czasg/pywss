# coding: utf-8
import time


def logCost(ctx):
    entry = time.time()
    ctx.next()
    ctx.log().withFields({"cost": f"{time.time() - entry}"}).info("exit")
