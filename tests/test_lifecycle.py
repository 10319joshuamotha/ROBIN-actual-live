from robin.lifecycle import Lifecycle, LifecycleState


def test_sleep_requires_esc_to_wake() -> None:
    lifecycle = Lifecycle()
    lifecycle.start()
    lifecycle.sleep()

    assert lifecycle.state is LifecycleState.SLEEPING
    assert lifecycle.wake("ENTER") is False
    assert lifecycle.state is LifecycleState.SLEEPING
    assert lifecycle.wake("ESC") is True
    assert lifecycle.state is LifecycleState.LISTENING


def test_sleep_blocks_normal_state_changes() -> None:
    lifecycle = Lifecycle()
    lifecycle.start()
    lifecycle.sleep()
    lifecycle.begin_action()
    assert lifecycle.state is LifecycleState.SLEEPING
