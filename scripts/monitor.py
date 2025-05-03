import psutil
import pynvml
from gradio import Button, Textbox

from modules import scripts
from modules.script_callbacks import on_before_ui, on_script_unloaded, on_ui_settings
from modules.shared import OptionInfo, opts

HANDLE = None


def init():
    pynvml.nvmlInit()
    global HANDLE
    HANDLE = pynvml.nvmlDeviceGetHandleByIndex(opts.monitor_gpu_id)


def shutdown():
    global HANDLE
    HANDLE = None
    pynvml.nvmlShutdown()


def get_usage() -> str:
    cpu_percent = int(max(*psutil.cpu_percent(interval=None, percpu=True)))
    ram_info = psutil.virtual_memory()
    ram_percent = int(ram_info.percent)

    gpu_info = pynvml.nvmlDeviceGetUtilizationRates(HANDLE)
    gpu_percent = int(gpu_info.gpu)
    vram_info = pynvml.nvmlDeviceGetMemoryInfo(HANDLE)
    vram_percent = int(vram_info.used * 100.0 / vram_info.total)

    return f"{cpu_percent}, {ram_percent}, {gpu_percent}, {vram_percent}"


class Monitor(scripts.Script):
    def title(self):
        return "Resource Monitor"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if is_img2img else None

    def ui(self, is_img2img):
        if not is_img2img:
            return None

        info = Textbox(value="", elem_id="hw_info", interactive=False, visible=False)
        info.do_not_save_to_config = True
        btn = Button(value="Info", elem_id="hw_btn", interactive=True, visible=False)
        btn.do_not_save_to_config = True

        btn.click(
            fn=get_usage,
            outputs=[info],
            show_progress="hidden",
            preprocess=False,
            postprocess=False,
            queue=False,
        )

        return None


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
on_script_unloaded(shutdown)
