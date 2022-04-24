// ==UserScript==
// @name         YATA - Losses
// @namespace    https://yata.yt/
// @version      0.2
// @icon64       data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxMzUuNDcgMTM1LjQ3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxnIHRyYW5zZm9ybT0ibWF0cml4KC45OTkwOSAwIDAgLjk5OTk4IDQuNzk1NmUtNiAtMi4zNTg4ZS03KSI+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTE1IDQ2LjE0NCkiPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQuMDg4OWUtNiAxLjg1MjEpIj48cmVjdCB4PSItMTE0Ljg4IiB5PSItNDcuOTk2IiB3aWR0aD0iMTM1LjQ3IiBoZWlnaHQ9IjEzNS40NyIgZmlsbD0iI2IzYjNiMyIgc3R5bGU9InBhaW50LW9yZGVyOm5vcm1hbCIvPjxwYXRoIGQ9Im0tMTE0Ljc4LTQ3Ljk5M2gxMzUuMjVzLTEzNC43NSAxMzYuNDYtMTM1LjI1IDEzNS40NmMtMC40OTc3Mi0wLjk5NzAyIDAtMTM1LjQ2IDAtMTM1LjQ2eiIgZmlsbD0iIzQ0N2U5YiIvPjwvZz48L2c+PGcgdHJhbnNmb3JtPSJtYXRyaXgoMS4yMzU0IDAgMCAxLjI0MjYgLTI2LjMyMSAtMjMuMDY4KSI+PHBhdGggdHJhbnNmb3JtPSJtYXRyaXgoMS4wNiAwIDAgMS4wNTM5IC00LjI5ODYgLTYuODEzMikiIGQ9Im0xMjEuMzggNzUuODAzYTQ1LjQ1OSA0NS40NTkgMCAwIDEtNDUuNDU5IDQ1LjQ1OSA0NS40NTkgNDUuNDU5IDAgMCAxLTQ1LjQ1OS00NS40NTkgNDUuNDU5IDQ1LjQ1OSAwIDAgMSA0NS40NTktNDUuNDU5IDQ1LjQ1OSA0NS40NTkgMCAwIDEgNDUuNDU5IDQ1LjQ1OXoiIGZpbGw9IiMzNjM2MzYiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+PC9nPjxnIHRyYW5zZm9ybT0ibWF0cml4KC45OTI3NCAwIDAgLjk3MzUyIC03LjQxNTIgLTExLjE2NCkiIHN0cm9rZT0iIzM2MzYzNiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49ImJldmVsIiBzdHJva2Utd2lkdGg9IjEuNjExOCIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiPjxwYXRoIHRyYW5zZm9ybT0ibWF0cml4KDEuMjM1NCAwIDAgMS4yNDI2IC0xOC4xOTIgLTEzLjE0NykiIGQ9Im03Ni4wNDggNzUuOCAxNS4wOC0zMy4zMDRoMTYuMzI0bC0yMy43OSA0Ny4xMTN2MjYuODA2aC0xNS4xOHYtMjYuODA2bC0yMy43OS00Ny4xMTNoMTYuMzc0eiIgZmlsbD0iI2IzYjNiMyIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCB0cmFuc2Zvcm09Im1hdHJpeCgxLjIzNTQgMCAwIDEuMjQyNiAtMTguMTkyIC0xMy4xNDcpIiBkPSJtNjguNDgzIDg5LjYwOS00LjQxMzQtOC45MjU4YzAuODg0NjYtOC4wMjY0IDEuOTIzOC05LjIxNjggOC40ODk2LTEyLjI4MmwzLjUxODEgNy43NDQzIDQuNzgyMi0xMC4wNTZzNi43NTc2LTIuNTg4IDExLjMzNy04LjQ5MTRjNC4zMzIzLTUuNTg1MyA0LjMyNDktMTUuMzIxIDQuMzI0OS0xNS4zMjFsMTAuOTMxIDAuMjE4NzEtMjMuNzkgNDcuMTEzdjI2LjgwNmgtMTUuMThjMy4zMWUtNCAtOC4wMDQgMC0yNi44MDYgMC0yNi44MDZ6IiBmaWxsPSIjNDQ3ZTliIiBzdHlsZT0icGFpbnQtb3JkZXI6bWFya2VycyBmaWxsIHN0cm9rZSIvPjwvZz48ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLjQwNjggLS4wNTY0NDcgLjA2NDk1OSAxLjMxMDEgLTM5LjM1NyAtMjQuMDY2KSIgZmlsbD0iIzQ0N2U5YiI+PHBhdGggZD0ibTk0Ljk1MiA5NC4yMDQtMi44MDkzIDUuMjU4OCAyLjQwNDggMi42MjM4LTEuNzAzOCAzLjE4OTMtMTEuMzY5LTEzLjMwMSAxLjQ4NDgtMi43Nzk0IDE3LjE3NCAyLjQzMzMtMS43MDM4IDMuMTg5M3ptLTQuNzU3MiAzLjEzMzUgMS45NDQxLTMuNjM5MS02LjMxNjQtMS4xMjA4eiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCBkPSJtOTQuMiA3My45MjYtMi4zODIgNC40NTg5IDExLjg4MyA2LjU2NjUtMS42MDIzIDIuOTk5My0xMS44ODMtNi41NjY1LTIuMzUgNC4zOTktMi4zODA1LTEuMzE1NSA2LjMzNDQtMTEuODU3eiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCBkPSJtMTA3LjgxIDcwLjEzLTIuODA5MyA1LjI1ODggMi40MDQ4IDIuNjIzOC0xLjcwMzggMy4xODkzLTExLjM2OS0xMy4zMDEgMS40ODQ4LTIuNzc5NCAxNy4xNzQgMi40MzMzLTEuNzAzOCAzLjE4OTN6bS00Ljc1NzIgMy4xMzM1IDEuOTQ0MS0zLjYzOTEtNi4zMTY0LTEuMTIwOHoiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+PC9nPjwvZz48L3N2Zz4K
// @description  Set bulk losses price
// @run-at       document-end
// @updateURL    https://github.com/Kivou-2000607/yata/raw/master/yata/static/yata/js/userscripts/losses.user.js
// @downloadURL  https://github.com/Kivou-2000607/yata/raw/master/yata/static/yata/js/userscripts/losses.user.js
// @author       Pyrit [2111649] & Kivou [2000607] (for the shitty part)
// @match        https://www.torn.com/sendcash.php*
// @grant        none
// ==/UserScript==

// change your price for a single loss here
const price = 250000;

function changeValue() {
    const money = document.querySelector(".input-money:nth-child(2)");
    const message = document.querySelector("input.message:nth-child(2)");
    const losses = window.location.href.split("&")[1].split("=")[1];
    money.value = price * losses;
    message.value = parseInt(losses) === 1 ? `${losses} loss. Thanks.` : `${losses} losses. Thanks.`;
}

(() => {
    const wrap = document.body.querySelector(".sendcash-form-wrap");
    if (wrap === null) {
        const wrapObserver = new MutationObserver((records) => {
            if (records.some((record) => record.type === "childList" &&
				record.target instanceof Element &&
				record.target.classList.contains("input-money-group"))
			) {
                wrapObserver.disconnect();
                changeValue();
            }
        });
        wrapObserver.observe(document.body, { subtree: true, childList: true });
    } else changeValue();
})();
