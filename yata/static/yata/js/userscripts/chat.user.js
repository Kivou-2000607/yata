// ==UserScript==
// @name         YATA - Chats
// @namespace    https://yata.yt/
// @version      0.9
// @icon64       data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxMzUuNDcgMTM1LjQ3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxnIHRyYW5zZm9ybT0ibWF0cml4KC45OTkwOSAwIDAgLjk5OTk4IDQuNzk1NmUtNiAtMi4zNTg4ZS03KSI+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTE1IDQ2LjE0NCkiPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQuMDg4OWUtNiAxLjg1MjEpIj48cmVjdCB4PSItMTE0Ljg4IiB5PSItNDcuOTk2IiB3aWR0aD0iMTM1LjQ3IiBoZWlnaHQ9IjEzNS40NyIgZmlsbD0iI2IzYjNiMyIgc3R5bGU9InBhaW50LW9yZGVyOm5vcm1hbCIvPjxwYXRoIGQ9Im0tMTE0Ljc4LTQ3Ljk5M2gxMzUuMjVzLTEzNC43NSAxMzYuNDYtMTM1LjI1IDEzNS40NmMtMC40OTc3Mi0wLjk5NzAyIDAtMTM1LjQ2IDAtMTM1LjQ2eiIgZmlsbD0iIzQ0N2U5YiIvPjwvZz48L2c+PGcgdHJhbnNmb3JtPSJtYXRyaXgoMS4yMzU0IDAgMCAxLjI0MjYgLTI2LjMyMSAtMjMuMDY4KSI+PHBhdGggdHJhbnNmb3JtPSJtYXRyaXgoMS4wNiAwIDAgMS4wNTM5IC00LjI5ODYgLTYuODEzMikiIGQ9Im0xMjEuMzggNzUuODAzYTQ1LjQ1OSA0NS40NTkgMCAwIDEtNDUuNDU5IDQ1LjQ1OSA0NS40NTkgNDUuNDU5IDAgMCAxLTQ1LjQ1OS00NS40NTkgNDUuNDU5IDQ1LjQ1OSAwIDAgMSA0NS40NTktNDUuNDU5IDQ1LjQ1OSA0NS40NTkgMCAwIDEgNDUuNDU5IDQ1LjQ1OXoiIGZpbGw9IiMzNjM2MzYiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+PC9nPjxnIHRyYW5zZm9ybT0ibWF0cml4KC45OTI3NCAwIDAgLjk3MzUyIC03LjQxNTIgLTExLjE2NCkiIHN0cm9rZT0iIzM2MzYzNiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49ImJldmVsIiBzdHJva2Utd2lkdGg9IjEuNjExOCIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiPjxwYXRoIHRyYW5zZm9ybT0ibWF0cml4KDEuMjM1NCAwIDAgMS4yNDI2IC0xOC4xOTIgLTEzLjE0NykiIGQ9Im03Ni4wNDggNzUuOCAxNS4wOC0zMy4zMDRoMTYuMzI0bC0yMy43OSA0Ny4xMTN2MjYuODA2aC0xNS4xOHYtMjYuODA2bC0yMy43OS00Ny4xMTNoMTYuMzc0eiIgZmlsbD0iI2IzYjNiMyIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCB0cmFuc2Zvcm09Im1hdHJpeCgxLjIzNTQgMCAwIDEuMjQyNiAtMTguMTkyIC0xMy4xNDcpIiBkPSJtNjguNDgzIDg5LjYwOS00LjQxMzQtOC45MjU4YzAuODg0NjYtOC4wMjY0IDEuOTIzOC05LjIxNjggOC40ODk2LTEyLjI4MmwzLjUxODEgNy43NDQzIDQuNzgyMi0xMC4wNTZzNi43NTc2LTIuNTg4IDExLjMzNy04LjQ5MTRjNC4zMzIzLTUuNTg1MyA0LjMyNDktMTUuMzIxIDQuMzI0OS0xNS4zMjFsMTAuOTMxIDAuMjE4NzEtMjMuNzkgNDcuMTEzdjI2LjgwNmgtMTUuMThjMy4zMWUtNCAtOC4wMDQgMC0yNi44MDYgMC0yNi44MDZ6IiBmaWxsPSIjNDQ3ZTliIiBzdHlsZT0icGFpbnQtb3JkZXI6bWFya2VycyBmaWxsIHN0cm9rZSIvPjwvZz48ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLjQwNjggLS4wNTY0NDcgLjA2NDk1OSAxLjMxMDEgLTM5LjM1NyAtMjQuMDY2KSIgZmlsbD0iIzQ0N2U5YiI+PHBhdGggZD0ibTk0Ljk1MiA5NC4yMDQtMi44MDkzIDUuMjU4OCAyLjQwNDggMi42MjM4LTEuNzAzOCAzLjE4OTMtMTEuMzY5LTEzLjMwMSAxLjQ4NDgtMi43Nzk0IDE3LjE3NCAyLjQzMzMtMS43MDM4IDMuMTg5M3ptLTQuNzU3MiAzLjEzMzUgMS45NDQxLTMuNjM5MS02LjMxNjQtMS4xMjA4eiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCBkPSJtOTQuMiA3My45MjYtMi4zODIgNC40NTg5IDExLjg4MyA2LjU2NjUtMS42MDIzIDIuOTk5My0xMS44ODMtNi41NjY1LTIuMzUgNC4zOTktMi4zODA1LTEuMzE1NSA2LjMzNDQtMTEuODU3eiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz48cGF0aCBkPSJtMTA3LjgxIDcwLjEzLTIuODA5MyA1LjI1ODggMi40MDQ4IDIuNjIzOC0xLjcwMzggMy4xODkzLTExLjM2OS0xMy4zMDEgMS40ODQ4LTIuNzc5NCAxNy4xNzQgMi40MzMzLTEuNzAzOCAzLjE4OTN6bS00Ljc1NzIgMy4xMzM1IDEuOTQ0MS0zLjYzOTEtNi4zMTY0LTEuMTIwOHoiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+PC9nPjwvZz48L3N2Zz4K
// @description  THIS IS A PRIVATE SCRIPT. DON'T USE IT. IT SENDS WEBSOCKET CHAT SECRET TO THE YATA DATABASE.
// @author       Kivou [2000607]
// @run-at       document-end
// @match        https://www.torn.com/*
// @grant        GM_xmlhttpRequest
// @connect      yata.yt
// @updateURL    https://github.com/Kivou-2000607/yata/raw/master/yata/static/yata/js/userscripts/chat.user.js
// @downloadURL  https://github.com/Kivou-2000607/yata/raw/master/yata/static/yata/js/userscripts/chat.user.js
// ==/UserScript==

var CHECK = '';

function setCookie() {
  var d = new Date();
  d.setTime(d.getTime() + (60*60*1000)); // expire after 1 hour
  document.cookie = "yatachatsecret=true;expires="+ d.toUTCString()+";path=/";
}

var errorColor = "#b3382c"
var validColor = "#4d7c1e"

function displayMessage(msg, color) {
    var messageDIV = document.createElement("div");
    messageDIV.innerText = msg;
    messageDIV.setAttribute("style", "line-height: 30px; text-align:center; font-weight: bold; color: "+color+";");

    var container = document.getElementsByClassName("header-wrapper-bottom")[0];
    container.appendChild(messageDIV);
}

(function() {
  'use strict';

    var check_cookie = (document.cookie.match(/^(?:.*;)?\s*yatachatsecret\s*=\s*([^;]+)(?:.*)?$/)||[,null])[1]

    if(check_cookie == null) {
        var secret = document.querySelector('script[src^="/js/chat/chat"').getAttribute("secret");
        var uid = document.querySelector('script[src^="/js/chat/chat"').getAttribute("uid");
        var check = CHECK;

        GM_xmlhttpRequest({
            method: "POST",
            url: "https://yata.yt/bot/secret/",
            //url: "http://127.0.0.1:8000/bot/secret/",
            headers: {"secret": secret, "uid": uid, "check": check},
            onload: resp=> {
                let obj = JSON.parse(resp.responseText);
                if ("message" in obj) {
                    if ("type" in obj && obj.type>0) {
                        displayMessage("YATA SECRET: " + obj.message, validColor);
                        setCookie();
                    }
                    else {
                        displayMessage("YATA SECRET: " + obj.message, errorColor);
                    }
                } else {
                    displayMessage("YATA SECRET: Error", errorColor);
                }
            },
            ontimeout: ()=>{
                displayMessage("YATA SECRET: Request has timed out", errorColor);
            },
            onerror: ()=>{
                displayMessage("YATA SECRET: Unknown error has occured when trying to send the data", errorColor);
            },
            onabort: ()=>{
                displayMessage("YATA SECRET: Upon sending the data, the request was canceled", errorColor);
            }
        });


    }
    //else {
    //    displayMessage("YATA SECRET: secret already sent recently", validColor);
    //}

})();
