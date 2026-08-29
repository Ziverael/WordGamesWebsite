function formatDateTime(date) {
    const pad = n => String(n).padStart(2, "0");
    return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ` +
        `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}
document.querySelectorAll(".local-time").forEach(el => {
    const date = new Date(el.dateTime);
    if (!Number.isNaN(date.getTime())) {
        el.textContent = formatDateTime(date);
    }
    else{
        console.warn("Invalid datetime:", el.dateTime);
    }
});
