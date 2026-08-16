const gameType = document.getElementById("type");
const layoutOptions = document.getElementById("layout");

function renderLayouts() {
    const selectedType = gameType.value;
    const layouts = layoutLabels[selectedType] ?? [];
    layoutOptions.innerHTML = "";

    for (const layout of layouts) {
        const label = document.createElement("label");

        label.className = "layout-card";

        label.innerHTML = `
        <div class="form-option">
        <div class="layout-name">
        ${layoutLabels[layout] ?? layout}
        </div>
        <div class="layout-graphic">
        <img src=${layoutImages[layout]} alt="${layout} schema picture"/>
        <!-- graphic goes here -->
        </div>
        <input
        type="radio"
        name="layout"
        value="${layout}"
        >


        </div>
        `;

        console.log(label)
        layoutOptions.appendChild(label);
    }
}


gameType.addEventListener("change", renderLayouts);

renderLayouts();
