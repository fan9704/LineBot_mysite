import logging
from django.db import transaction

@transaction.atomic
def transfer_money(_from, _to, quota):
    if _from.money < 15:
        raise ValueError("連手續費都付不起，請回吧!!")
    # 收取手續費
    _from.money = _from.money - 15
    _from.save()
    # 取得回滾的基準點
    sid = transaction.savepoint()
    try:
        _from.money = _from.money - quota
        if _from.money < 0:
            raise ValueError("超額提領!")
        _from.save()
        _to.money = _to.money + quota
        if _to.money > 100000:
            raise ValueError("超額儲存!")
        _to.save()
        # 如果操作及檢查都沒有問題，那就把資料提交到資料庫
        transaction.savepoint_commit(sid)
    except ValueError as e:
        logging.error("金額操作錯誤，訊息:<%s>", e)
        # 當發生問題時回滾到之前的基準點，還原先前操作影響的資料
        transaction.savepoint_rollback(sid)
    except Exception as e:
        logging.error("其他錯誤，訊息:<%s>", e)
        transaction.savepoint_rollback(sid)
