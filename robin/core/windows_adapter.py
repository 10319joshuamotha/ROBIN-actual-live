from __future__ import annotations

import subprocess
import sys

from .action import ActionPlan


class WindowsActionAdapter:
    """Execute the tiny, explicit Windows application allowlist without a shell."""

    APPLICATIONS = {
        "calculator": ["calc.exe"],
        "notepad": ["notepad.exe"],
        "file explorer": ["explorer.exe"],
    }

    def execute(self, plan: ActionPlan) -> str:
        if plan.request.action != "open_application":
            raise ValueError("This adapter only supports opening an allowlisted application.")

        app = " ".join(plan.request.resource.strip().casefold().split())
        command = self.APPLICATIONS.get(app)
        if command is None:
            raise ValueError("That application is not allowlisted.")
        if sys.platform != "win32":
            raise RuntimeError("Desktop control is available only from the Windows runtime.")

        subprocess.Popen(command, shell=False, close_fds=True)
        return f"Opened {app}."
