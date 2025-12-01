document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length) {
        setTimeout(() => {
            alerts.forEach((alert) => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            });
        }, 4000);
    }

    const shell = document.getElementById("page-shell");

    // Page transition for internal links
    if (shell) {
        const links = document.querySelectorAll("a[href]");
        links.forEach((link) => {
            const href = link.getAttribute("href");
            if (!href || href.startsWith("#")) return;
            if (link.dataset.noTransition === "true") return;

            const url = new URL(link.href, window.location.href);
            if (url.origin !== window.location.origin) return;
            if (link.target === "_blank" || link.hasAttribute("download")) return;

            link.addEventListener("click", function (e) {
                e.preventDefault();
                shell.classList.add("page-exit");
                setTimeout(() => {
                    window.location.href = link.href;
                }, 250);
            });
        });
    }

    // Mouse move glow (CSS variables)
    document.addEventListener("mousemove", function (e) {
        const x = (e.clientX / window.innerWidth) * 100;
        const y = (e.clientY / window.innerHeight) * 100;
        document.documentElement.style.setProperty("--mx", `${x}%`);
        document.documentElement.style.setProperty("--my", `${y}%`);
    });
});
