// ==UserScript==
// @name         YATA - Losses
// @namespace    https://yata.yt/
// @version      0.1.1
// @icon64       data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTMuMTAxbW0iIGhlaWdodD0iOTMuMTAxbW0iIHZlcnNpb249IjEuMSIgdmlld0JveD0iMCAwIDkzLjEwMSA5My4xMDEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgogPGRlZnM+CiAgPGxpbmVhckdyYWRpZW50IGlkPSJsaW5lYXJHcmFkaWVudDg2MSIgeDE9IjQwLjQ4MSIgeDI9IjQwLjQ4MSIgeTE9IjkyLjYwNCIgeTI9Ii0uNTI5MTYiIGdyYWRpZW50VHJhbnNmb3JtPSJ0cmFuc2xhdGUoLjc3NzUxIC43Nzc1MSkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiBzcHJlYWRNZXRob2Q9InJlcGVhdCI+CiAgIDxzdG9wIHN0b3AtY29sb3I9IiM3NTc1NzUiIG9mZnNldD0iMCIvPgogICA8c3RvcCBzdG9wLWNvbG9yPSIjZmZmIiBvZmZzZXQ9IjEiLz4KICA8L2xpbmVhckdyYWRpZW50PgogIDxmaWx0ZXIgaWQ9ImZpbHRlcjg3MSIgeD0iLS4wMTIiIHk9Ii0uMDEyIiB3aWR0aD0iMS4wMjQiIGhlaWdodD0iMS4wMjQiIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiI+CiAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjAuNDU0NTk0MDQiLz4KICA8L2ZpbHRlcj4KIDwvZGVmcz4KIDxwYXRoIGQ9Im05Mi4wMSA0Ni41NWE0NS40NTkgNDUuNDU5IDAgMCAxLTQ1LjQ1OSA0NS40NTkgNDUuNDU5IDQ1LjQ1OSAwIDAgMS00NS40NTktNDUuNDU5IDQ1LjQ1OSA0NS40NTkgMCAwIDEgNDUuNDU5LTQ1LjQ1OSA0NS40NTkgNDUuNDU5IDAgMCAxIDQ1LjQ1OSA0NS40NTl6IiBmaWxsPSJ1cmwoI2xpbmVhckdyYWRpZW50ODYxKSIgZmlsdGVyPSJ1cmwoI2ZpbHRlcjg3MSkiIHN0cm9rZT0iIzQ0N2U5YiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjEuODQ0MSIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KIDxnIHRyYW5zZm9ybT0ibWF0cml4KDE5LjQ3OSAwIDAgMTkuNDc5IDIzMDQuMiAtMjU0OS44KSI+CiAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoLjA0NDExNyAwIDAgLjA0NDExNyAtMTEyLjQxIDEyOS42MikiPgogICA8cGF0aCBkPSJtLTc5LjE1NiA4Ni4zNTEgMTcuNTQ4LTM4Ljc1NWgxOC45OTZsLTI3LjY4MyA1NC44MjR2MzEuMTkzaC0xNy42NjR2LTMxLjE5M2wtMjcuNjgzLTU0LjgyNGgxOS4wNTR6IiBmaWxsPSIjNDQ3ZTliIiBzdHJva2U9IiM0MTRjNTEiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzLjk0MjIiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+CiAgPC9nPgogPC9nPgogPGcgdHJhbnNmb3JtPSJtYXRyaXgoLjQ3NDIgLS44ODc2NiAuODY5NzkgLjQ4MDY0IDAgMCkiIGZpbGw9IiM0MTRjNTEiIHN0cm9rZT0iI2FkYWRhZCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9Ii42NTY2OCIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiIGFyaWEtbGFiZWw9IkFUQSI+CiAgPHBhdGggZD0ibS0yNS4yODUgOTYuMDE1aC01LjkyNDNsLTEuMTI2MyAzLjM3ODloLTMuNTkyOWw2LjEwNDUtMTYuMzk5aDMuMTMxMWw2LjEzODMgMTYuMzk5aC0zLjU5Mjl6bS01LjAxMi0yLjczNjloNC4wOTk3bC0yLjA2MTEtNi4xMzgzeiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KICA8cGF0aCBkPSJtLTguMDA4MiA4NS43MzJoLTUuMDIzMnYxMy42NjJoLTMuMzc4OXYtMTMuNjYyaC00Ljk1NTd2LTIuNzM2OWgxMy4zNTh6IiBzdHlsZT0icGFpbnQtb3JkZXI6bWFya2VycyBmaWxsIHN0cm9rZSIvPgogIDxwYXRoIGQ9Im0xLjgzNTUgOTYuMDE1aC01LjkyNDNsLTEuMTI2MyAzLjM3ODloLTMuNTkyOWw2LjEwNDUtMTYuMzk5aDMuMTMxMWw2LjEzODMgMTYuMzk5aC0zLjU5Mjl6bS01LjAxMi0yLjczNjloNC4wOTk3bC0yLjA2MTEtNi4xMzgzeiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KIDwvZz4KPC9zdmc+Cg==
// @description  Set bulk losses price
// @run-at       document-end
// @author       Pyrit [2111649] & Kivou [2000607] (for the shitty part)
// @match        https://www.torn.com/sendcash.php*
// @grant        none
// ==/UserScript==

// change your price for a single loss here
const price = 250000;

const changeValue = () => {
    const money = document.querySelector(".input-money:nth-child(2)");
    const message = document.querySelector("input.message:nth-child(2)");
    const losses = window.location.href.split("&")[1].split("=")[1];
    money.value = price * losses;
    message.value = losses == 1 ? `${losses} loss. Thanks.` : `${losses} losses. Thanks.`;
};

(function() {
    const wrap = document.body.querySelector(".sendcash-form-wrap");
    if (wrap === null) {
        const wrapObserver = new MutationObserver((records) => {
            if (records.some((record) => record.type == "childList"
                && record.target instanceof Element
                && record.target.classList.contains("input-money-group"))) {

                wrapObserver.disconnect();
                changeValue()
            }
        });
        wrapObserver.observe(document.body, { subtree: true, childList: true });
    } else {
        changeValue();
    }
})();
