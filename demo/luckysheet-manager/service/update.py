# coding: utf-8
import queue
import loggus

from db.mongo import collection as mongodb

lucky_sheet_queue = queue.Queue()


def update_worker():
    while True:
        (excel_id, data) = lucky_sheet_queue.get()
        typ = data["t"]
        index = data["i"]
        value = data["v"]

        if typ in ("v", "fu", "fm"):  # 单元格更新
            row = data["r"]
            col = data["c"]
            mongodb.update_one(
                {
                    "id": excel_id,
                    "data": {
                        "$elemMatch": {
                            "index": index,
                        },
                    },
                },
                {
                    "$set": {
                        f"data.$.data.{row}.{col}": value,
                    },
                },
                upsert=True,
            )
        elif typ == "rv":  # 范围单元格数据更新
            row_0, row_1 = data["range"]["row"]
            col_0, col_1 = data["range"]["column"]
            for i in range(row_0, row_1 + 1):
                for j in range(col_0, col_1 + 1):
                    mongodb.update_one(
                        {
                            "id": excel_id,
                            "data": {
                                "$elemMatch": {
                                    "index": index,
                                },
                            },
                        },
                        {
                            "$set": {
                                f"data.$.data.{i}.{j}": value[i - row_0][j - col_0],
                            },
                        },
                        upsert=True,
                    )
        elif typ in ("rv_end"):  # 忽略
            pass
        elif typ == "all":  # 通用更新
            key = data["k"]
            mongodb.update_one(
                {
                    "id": excel_id,
                    "data": {
                        "$elemMatch": {
                            "index": index,
                        },
                    },
                },
                {
                    "$set": {
                        f"data.$.{key}": value,
                    },
                },
                upsert=True,
            )
        elif typ == "cg":  # 配置更新
            key = data["k"]
            mongodb.update_one(
                {
                    "id": excel_id,
                    "data": {
                        "$elemMatch": {
                            "index": index,
                        },
                    },
                },
                {
                    "$set": {
                        f"data.$.config.{key}": value,
                    },
                },
                upsert=True,
            )
        elif typ == "sha":  # 新建页
            value["data"] = [[None for _ in range(value["column"])] for _ in range(value["row"])]
            mongodb.update_one(
                {
                    "id": excel_id,
                },
                {
                    "$push": {
                        "data": value,
                    },
                },
                upsert=True,
            )
        else:
            loggus.update(typ=typ, data=data).warning(f"暂不支持操作类型")
