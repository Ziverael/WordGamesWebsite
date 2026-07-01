// Simple UI enhancement effects

document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".glass-card");

    cards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.style.transform = "translateY(-5px)";
            card.style.transition = "0.3s";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "translateY(0)";
        });
    })
});
