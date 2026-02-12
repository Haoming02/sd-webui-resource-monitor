import psutil
import pynvml
from fastapi import FastAPI

from modules.script_callbacks import (
    on_app_started,
    on_before_ui,
    on_script_unloaded,
    on_ui_settings,
)
from modules.shared import OptionInfo, opts

HANDLE = None


def init():
    pynvml.nvmlInit()
    global HANDLE
    HANDLE = pynvml.nvmlDeviceGetHandleByIndex(getattr(opts, "monitor_gpu_id", 0))


def shutdown():
    global HANDLE
    HANDLE = None
    pynvml.nvmlShutdown()


def monitor_api(_, app: FastAPI):

    @app.get("/resource/monitor")
    def get_usage() -> str:
        cpu_percent = int(psutil.cpu_percent(interval=None))
        ram_info = psutil.virtual_memory()
        ram_percent = int(ram_info.percent)

        gpu_info = pynvml.nvmlDeviceGetUtilizationRates(HANDLE)
        gpu_percent = int(gpu_info.gpu)
        vram_info = pynvml.nvmlDeviceGetMemoryInfo(HANDLE)
        vram_percent = int(vram_info.used * 100.0 / vram_info.total)

        return f"{cpu_percent}, {ram_percent}, {gpu_percent}, {vram_percent}"


def settings():
    args = {"section": ("hm", "Hardware Monitor"), "category_id": "system"}

    opts.add_option(
        "monitor_gpu_id",
        OptionInfo(0, "GPU ID", **args)
        .info("the ID to monitor in a multi-GPU system")
        .needs_reload_ui(),
    )

    opts.add_option(
        "monitor_polling_rate",
        OptionInfo(1000, "Polling Rate", **args)
        .info("interval (ms) between each refresh")
        .needs_reload_ui(),
    )


on_before_ui(init)
on_ui_settings(settings)
on_app_started(monitor_api)
on_script_unloaded(shutdown)
