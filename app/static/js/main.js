document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    const menuButton = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#primary-nav");
    if (menuButton && navigation) {
        menuButton.addEventListener("click", () => {
            const isOpen = menuButton.getAttribute("aria-expanded") === "true";
            menuButton.setAttribute("aria-expanded", String(!isOpen));
            navigation.classList.toggle("is-open", !isOpen);
            menuButton.querySelector("[data-lucide]")?.setAttribute("data-lucide", isOpen ? "menu" : "x");
            window.lucide?.createIcons();
        });
        navigation.addEventListener("click", (event) => {
            if (event.target.closest("a")) {
                menuButton.setAttribute("aria-expanded", "false");
                navigation.classList.remove("is-open");
            }
        });
    }

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", () => button.closest(".flash")?.remove());
    });
});
