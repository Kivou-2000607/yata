// ==UserScript==
// @name         YATA - Chats
// @namespace    https://yata.yt/
// @version      0.5
// @icon64       data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTMuMTAxbW0iIGhlaWdodD0iOTMuMTAxbW0iIHZlcnNpb249IjEuMSIgdmlld0JveD0iMCAwIDkzLjEwMSA5My4xMDEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgogPGRlZnM+CiAgPGxpbmVhckdyYWRpZW50IGlkPSJsaW5lYXJHcmFkaWVudDg2MSIgeDE9IjQwLjQ4MSIgeDI9IjQwLjQ4MSIgeTE9IjkyLjYwNCIgeTI9Ii0uNTI5MTYiIGdyYWRpZW50VHJhbnNmb3JtPSJ0cmFuc2xhdGUoLjc3NzUxIC43Nzc1MSkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiBzcHJlYWRNZXRob2Q9InJlcGVhdCI+CiAgIDxzdG9wIHN0b3AtY29sb3I9IiM3NTc1NzUiIG9mZnNldD0iMCIvPgogICA8c3RvcCBzdG9wLWNvbG9yPSIjZmZmIiBvZmZzZXQ9IjEiLz4KICA8L2xpbmVhckdyYWRpZW50PgogIDxmaWx0ZXIgaWQ9ImZpbHRlcjg3MSIgeD0iLS4wMTIiIHk9Ii0uMDEyIiB3aWR0aD0iMS4wMjQiIGhlaWdodD0iMS4wMjQiIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiI+CiAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjAuNDU0NTk0MDQiLz4KICA8L2ZpbHRlcj4KIDwvZGVmcz4KIDxwYXRoIGQ9Im05Mi4wMSA0Ni41NWE0NS40NTkgNDUuNDU5IDAgMCAxLTQ1LjQ1OSA0NS40NTkgNDUuNDU5IDQ1LjQ1OSAwIDAgMS00NS40NTktNDUuNDU5IDQ1LjQ1OSA0NS40NTkgMCAwIDEgNDUuNDU5LTQ1LjQ1OSA0NS40NTkgNDUuNDU5IDAgMCAxIDQ1LjQ1OSA0NS40NTl6IiBmaWxsPSJ1cmwoI2xpbmVhckdyYWRpZW50ODYxKSIgZmlsdGVyPSJ1cmwoI2ZpbHRlcjg3MSkiIHN0cm9rZT0iIzQ0N2U5YiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjEuODQ0MSIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KIDxnIHRyYW5zZm9ybT0ibWF0cml4KDE5LjQ3OSAwIDAgMTkuNDc5IDIzMDQuMiAtMjU0OS44KSI+CiAgPGcgdHJhbnNmb3JtPSJtYXRyaXgoLjA0NDExNyAwIDAgLjA0NDExNyAtMTEyLjQxIDEyOS42MikiPgogICA8cGF0aCBkPSJtLTc5LjE1NiA4Ni4zNTEgMTcuNTQ4LTM4Ljc1NWgxOC45OTZsLTI3LjY4MyA1NC44MjR2MzEuMTkzaC0xNy42NjR2LTMxLjE5M2wtMjcuNjgzLTU0LjgyNGgxOS4wNTR6IiBmaWxsPSIjNDQ3ZTliIiBzdHJva2U9IiM0MTRjNTEiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzLjk0MjIiIHN0eWxlPSJwYWludC1vcmRlcjptYXJrZXJzIGZpbGwgc3Ryb2tlIi8+CiAgPC9nPgogPC9nPgogPGcgdHJhbnNmb3JtPSJtYXRyaXgoLjQ3NDIgLS44ODc2NiAuODY5NzkgLjQ4MDY0IDAgMCkiIGZpbGw9IiM0MTRjNTEiIHN0cm9rZT0iI2FkYWRhZCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9Ii42NTY2OCIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiIGFyaWEtbGFiZWw9IkFUQSI+CiAgPHBhdGggZD0ibS0yNS4yODUgOTYuMDE1aC01LjkyNDNsLTEuMTI2MyAzLjM3ODloLTMuNTkyOWw2LjEwNDUtMTYuMzk5aDMuMTMxMWw2LjEzODMgMTYuMzk5aC0zLjU5Mjl6bS01LjAxMi0yLjczNjloNC4wOTk3bC0yLjA2MTEtNi4xMzgzeiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KICA8cGF0aCBkPSJtLTguMDA4MiA4NS43MzJoLTUuMDIzMnYxMy42NjJoLTMuMzc4OXYtMTMuNjYyaC00Ljk1NTd2LTIuNzM2OWgxMy4zNTh6IiBzdHlsZT0icGFpbnQtb3JkZXI6bWFya2VycyBmaWxsIHN0cm9rZSIvPgogIDxwYXRoIGQ9Im0xLjgzNTUgOTYuMDE1aC01LjkyNDNsLTEuMTI2MyAzLjM3ODloLTMuNTkyOWw2LjEwNDUtMTYuMzk5aDMuMTMxMWw2LjEzODMgMTYuMzk5aC0zLjU5Mjl6bS01LjAxMi0yLjczNjloNC4wOTk3bC0yLjA2MTEtNi4xMzgzeiIgc3R5bGU9InBhaW50LW9yZGVyOm1hcmtlcnMgZmlsbCBzdHJva2UiLz4KIDwvZz4KPC9zdmc+Cg==
// @description  THIS IS A PRIVATE SCRIPT. DON'T USE IT. IT SENDS WEBSOCKET CHAT SECRET TO THE YATA DATABASE.
// @author       Kivou [2000607]
// @run-at       document-end
// @match        https://www.torn.com/*
// @grant        GM_xmlhttpRequest
// @connect      yata.yt
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
