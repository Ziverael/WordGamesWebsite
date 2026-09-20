async function checkNotifications() {
    try {
        const response = await fetch(
            "/api/notifications/unread-count",
            {
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json"
                }
            }
        );
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        updateInvitationBadge(data.invitations);

    } catch (error) {
        console.error("Notification check failed", error);
    }
}


function updateInvitationBadge(count) {
    const badge = document.querySelector("#invitation-badge");

    if (count > 0) {
        badge.textContent = count;
        badge.parentElement.classList.add("red");
    } else {
        badge.parentElement.classList.remove("red");
    }
}

checkNotifications();
const MINUTE_IN_MILISEC = 60_000
setInterval(checkNotifications, MINUTE_IN_MILISEC)
