from robin.lifecycle import LifecycleState
from robin.runtime import RobinRuntime


class FakeAdapter:
    def execute(self, plan):
        return f"executed:{plan.request.action}:{plan.request.resource}"


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


def test_runtime_executes_only_explicit_allowlisted_windows_commands() -> None:
    runtime = RobinRuntime(action_adapter=FakeAdapter())
    runtime.start()
    opened = runtime.handle("open calculator", user_command_id="user-command")
    assert opened.message == "executed:open_application:calculator"

    missing_context = runtime.handle("open calculator")
    assert "Action blocked" in missing_context.message

    unknown = runtime.handle("open powershell", user_command_id="user-command-2")
    assert "Action blocked" in unknown.message


def test_unknown_command_is_not_reported_as_accepted() -> None:
    result = RobinRuntime().handle("do anything", user_command_id="user-command")
    assert "Nothing was sent or changed" in result.message
