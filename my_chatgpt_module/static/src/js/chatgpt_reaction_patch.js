/** @odoo-module **/

import { rpc } from "@web/core/network/rpc_service";

console.log("👀 Reaction Monitor Loaded");

function attachReactionListeners(container) {
    const buttons = container.querySelectorAll(".o-mail-MessageReaction:not([data-tracked])");
    buttons.forEach((btn) => {
        btn.setAttribute("data-tracked", "1");

        btn.addEventListener("click", async () => {
            const emoji = btn.querySelector("span")?.textContent?.trim();
            const messageBox = btn.closest("[data-sheet-row]");
            const row = messageBox?.getAttribute("data-sheet-row");

            console.log("📦 Clicked:", emoji, "row:", row);

            if (emoji && row) {
                try {
                    await rpc.query({
                        model: "chatgpt.module",
                        method: "_update_feedback_by_row_number",
                        args: [parseInt(row), emoji],
                    });
                    console.log("✅ Reaction sent to update row:", row);
                } catch (err) {
                    console.error("❌ Failed to send reaction:", err);
                }
            } else {
                console.warn("⚠️ Missing emoji or sheet row number");
            }
        });
    });
}

function initReactionTracking() {
    const chat = document.querySelector(".o_Discuss");
    if (!chat) return;

    // Track already loaded buttons
    attachReactionListeners(chat);

    // Observe any new buttons added dynamically
    const observer = new MutationObserver(() => {
        attachReactionListeners(chat);
    });
    observer.observe(chat, { childList: true, subtree: true });
}

setTimeout(initReactionTracking, 1500);
