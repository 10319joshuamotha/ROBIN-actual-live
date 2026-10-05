from robin.lifecycle import LifecycleState
from robin.runtime import RobinRuntime


def test_runtime_starts_dormant() -> None:
    runtime = RobinRuntime()
    result = runtime.start()
    assert result.state is LifecycleState.DORMANT


def test_runtime_sleep_blocks_commands_until_esc() -> None:
    runtime = RobinRuntime()
    runtime.start()
    sleeping = runtime.handle("go to sleep")
    assert sleeping.state is LifecycleState.SLEEPING

    blocked = runtime.handle("status")
    assert blocked.state is LifecycleState.SLEEPING
    assert "ESC" in blocked.message

    awake = runtime.wake_with_key("ESC")
    assert awake.state is LifecycleState.LISTENING


def test_runtime_status_and_health() -> None:
    runtime = RobinRuntime()
    runtime.start()
    assert "dormant" in runtime.handle("status").message
    assert "OK" in runtime.handle("health").message
