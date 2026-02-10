document.addEventListener("DOMContentLoaded", () => {
    console.log("Admission Portal loaded");
});

function showPopup(message, type) {
    const popup = document.createElement("div");
    popup.className = "popup-message " + (type === "success" ? "popup-success" : "popup-error");
    popup.textContent = message;

    document.body.appendChild(popup);

    setTimeout(() => popup.classList.add("show"), 100);
    setTimeout(() => {
        popup.classList.remove("show");
        setTimeout(() => popup.remove(), 300);
    }, 2500);
}

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("flash-data");
    if (!container) return;

    const messages = JSON.parse(container.dataset.messages || "[]");

    messages.forEach(function ([category, message]) {
        showPopup(message, category);
    });
});


function togglePassword(icon) {
    const input = document.getElementById("password");

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("hide");
    } else {
        input.type = "password";
        icon.classList.add("hide");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const currentUrl = window.location.pathname;
    const links = document.querySelectorAll('.sidebar a');

    links.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentUrl) {
            link.classList.add('active');
        }
    });
});

// remark card 

function openRemarkModal(btn) {
    const leadId = btn.dataset.leadId;
    const remark = btn.dataset.remark || "";
    const updated = btn.dataset.updated || "";

    document.getElementById("lead_id").value = leadId;
    document.getElementById("remark").value = remark;

    document.getElementById("remarkUpdated").innerText =
        updated ? `Last updated: ${updated}` : "No previous remark";

    document.getElementById("remarkModal").style.display = "flex";
}

function closeRemarkModal() {
    document.getElementById("remarkModal").style.display = "none";
}

