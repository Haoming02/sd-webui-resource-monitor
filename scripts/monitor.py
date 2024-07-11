from modules import scripts, shared, script_callbacks
import gradio as gr
import psutil
import pynvml

HANDLE = None


def onInit():
    global HANDLE
    pynvml.nvmlInit()
    HANDLE = pynvml.nvmlDeviceGetHandleByIndex(
        getattr(shared.opts, "monitor_gpu_id", 0)
    )


def get_usage() -> str:
    cpu_percent: int = int(max(*psutil.cpu_percent(interval=None, percpu=True)))
    ram_info = psutil.virtual_memory()
    ram_percent: int = int(ram_info.percent)

    gpu_info = pynvml.nvmlDeviceGetUtilizationRates(HANDLE)
    gpu_percent: int = int(gpu_info.gpu)
    vram_info = pynvml.nvmlDeviceGetMemoryInfo(HANDLE)
    vram_percent: int = int(vram_info.used * 100.0 / vram_info.total)

    return f"{cpu_percent}, {ram_percent}, {gpu_percent}, {vram_percent}"


class Monitor(scripts.Script):

    def title(self):
        return "Resource Monitor"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if not is_img2img else None

    def ui(self, is_img2img):
        if is_img2img is True:
            return None

        with gr.Blocks():
            info = gr.Textbox(
                None,
                lines=1,
                max_lines=1,
                container=False,
                visible=False,
                interactive=False,
                elem_id="hw_info",
                autoscroll=False,
            )

            btn = gr.Button("Info", visible=False, interactive=True, elem_id="hw_btn")

        btn.click(
            fn=get_usage,
            inputs=None,
            outputs=[info],
            show_progress="hidden",
            preprocess=False,
            postprocess=False,
            queue=False,
        )

        return None


def on_ui_settings():
    section = ("hm", "Hardware Monitor")

    shared.opts.add_option(
        "monitor_gpu_id",
        shared.OptionInfo(
            0,
            "GPU ID",
            section=section,
        )
        .info("The ID to monitor in a multi-GPU system")
        .needs_reload_ui(),
    )

    shared.opts.add_option(
        "monitor_polling_rate",
        shared.OptionInfo(
            1000,
            "Polling Rate",
            section=section,
        )
        .info("Interval between each refresh of the charts [Unit: ms]")
        .needs_reload_ui(),
    )


script_callbacks.on_before_ui(onInit)
script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_script_unloaded(lambda: pynvml.nvmlShutdown())
