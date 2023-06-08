# coding: utf-8
import pywss

from pywss.constant import StatusInternalServerError


def NewRecoverHandler(
        status_code=StatusInternalServerError,
        default_content=None,
        traceback=False,
):
    def recoverHandler(ctx: pywss.Context):
        try:
            ctx.next()
        except:
            ctx.set_status_code(status_code)
            if default_content:
                ctx.write(default_content)
            if traceback:
                ctx.log.traceback()

    return recoverHandler
