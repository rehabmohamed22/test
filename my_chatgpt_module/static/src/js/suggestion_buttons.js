odoo.define('my_chatgpt_module.suggestion_buttons', [], function (require) {
    "use strict";

    console.log("📦 suggestion_buttons.js loaded ✅");

    setInterval(() => {
        document.querySelectorAll(".gpt-suggestion-btn").forEach((btn) => {
            if (!btn.dataset.bound) {
                btn.dataset.bound = "true";
                console.log("🔘 Bound to:", btn.innerText);

                btn.addEventListener("click", function () {
                    const question = btn.dataset.question || btn.textContent.trim();
                    console.log("🟢 Suggestion clicked:", question);

                    // نحاول نجيب الـ textarea بأي وسيلة ممكنة
                    const input = document.querySelector("textarea.o-mail-Compositor-input")
                                || document.querySelector("textarea.o_composer_textarea")
                                || document.querySelector("textarea");

                    if (input) {
                        input.value = question;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.focus();
                        console.log("✍️ Filled input with suggestion.");
                    } else {
                        console.error("❌ Still couldn't find any suitable input!");
                    }
                });
            }
        });
    }, 1000);
});
