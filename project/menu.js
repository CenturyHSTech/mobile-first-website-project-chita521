const toggleButton = document.querySelector(".nav-toggle");
const navMenu = document.querySelector(".nav-menu");

toggleButton.addEventListener("click", () => {
    navMenu.classList.toggle("active");

    const expanded =
        toggleButton.getAttribute("aria-expanded") === "true" || false;
    toggleButton.setAttribute("aria-expanded", !expanded);
});