from app.domain.work_order import WorkOrder, WorkStatus


def test_work_order_happy_path():
    wo = WorkOrder(os_id=1)
    wo.start_diagnosis()
    assert wo.status == WorkStatus.EM_DIAGNOSTICO
    wo.finish_diagnosis()
    wo.start_execution()
    assert wo.status == WorkStatus.EM_EXECUCAO
    wo.complete()
    assert wo.status == WorkStatus.DONE
