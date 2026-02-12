import launch

for dep in ("nvidia-ml-py", "psutil"):
    if not launch.is_installed(dep):
        launch.run_pip(f"install {dep}", f"{dep} for monitoring")
