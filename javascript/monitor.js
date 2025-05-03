(function () {
    const BAR_CHARTS = [
        ["CPU", "lime"],
        ["RAM", "green"],
        ["GPU", "cyan"],
        ["VRAM", "blue"],
    ];

    function createHardwareMonitor() {
        const canvas = document.createElement("div");
        canvas.id = "hw_monitor";

        const elements = [];

        const table = document.createElement("table");
        const colgroup = document.createElement("colgroup");

        const type = document.createElement("col");
        type.style.width = "25%";
        const bar = document.createElement("col");
        bar.style.width = "75%";

        colgroup.appendChild(type);
        colgroup.appendChild(bar);
        table.appendChild(colgroup);

        for (const [type, color] of BAR_CHARTS) {
            const row = table.insertRow();
            const title = row.insertCell();
            const chart = row.insertCell();

            title.textContent = type;

            const label = document.createElement("p");
            label.classList.add("hw-label");
            const bar = document.createElement("div");
            bar.style.background = color;

            chart.appendChild(label);
            chart.appendChild(bar);
            elements.push([label, bar]);
        }

        canvas.appendChild(table);

        canvas.setUsage = (c, r, g, v) => {
            elements[0][0].textContent = `${c}%`;
            elements[0][1].style.width = `${c}%`;
            elements[1][0].textContent = `${r}%`;
            elements[1][1].style.width = `${r}%`;
            elements[2][0].textContent = `${g}%`;
            elements[2][1].style.width = `${g}%`;
            elements[3][0].textContent = `${v}%`;
            elements[3][1].style.width = `${v}%`;
        };

        return canvas;
    }

    onUiLoaded(() => {
        const btn = gradioApp().getElementById("hw_btn");
        const rate = gradioApp()
            .getElementById("setting_monitor_polling_rate")
            .querySelector("input").value;
        const info = gradioApp()
            .getElementById("hw_info")
            .querySelector("textarea");

        const monitor = createHardwareMonitor();
        monitor.style.setProperty("--hw-bar-chart-speed", `${rate * 0.8}ms`);

        const quicksettings = gradioApp().getElementById("quicksettings");
        quicksettings.appendChild(monitor);

        setInterval(() => {
            const value = info.value.trim().split(", ");

            if (value.length > 1) {
                const cpu = Number.parseFloat(value[0]);
                const ram = Number.parseFloat(value[1]);
                const gpu = Number.parseFloat(value[2]);
                const vram = Number.parseFloat(value[3]);

                // console.table({ cpu, ram, gpu, vram });
                monitor.setUsage(cpu, ram, gpu, vram);
            }

            btn.click();
        }, rate);
    });
})();
