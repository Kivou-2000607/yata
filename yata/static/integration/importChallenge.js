// ==UserScript==
// @name         YATA Faction Upgrades
// @namespace    https://yata.alwaysdata.net/
// @version      0.0.1
// @icon64       data:image/svg+xml;base64,Cgk8c3ZnIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHZlcnNpb249IjEuMSIgd2lkdGg9IjEyOCIgaGVpZ2h0PSIxMjgiIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KCgoJCTxkZWZzPgoJCQk8bGluZWFyR3JhZGllbnQgaWQ9Imdsb3NzLTEtZ3JhZGllbnQiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iMTc2NC4yIiB5MT0iMjM5My43NSIgeDI9IjE3MTguMTAwMDAwMDAwMDAwMSIgeTI9IjI0MzkuODUwMDAwMDAwMDAwNCIgc3ByZWFkTWV0aG9kPSJwYWQiPgoJCQk8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjRkZGRkZGIiBzdG9wLW9wYWNpdHk9IjAuMjk4MDM5MjE1Njg2Mjc0NSIvPgoJCQk8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiIHN0b3Atb3BhY2l0eT0iMC4wOTgwMzkyMTU2ODYyNzQ1MSIvPgoJCTwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJnbG9zcy0yLWdyYWRpZW50IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjE4MDMuOCIgeTE9IjIzNjUuNjUiIHgyPSIxODAzLjgiIHkyPSIyNDc1LjM1IiBzcHJlYWRNZXRob2Q9InBhZCI+CgkJCTxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiIHN0b3Atb3BhY2l0eT0iMC4yOTgwMzkyMTU2ODYyNzQ1Ii8+CgkJCTxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0ZGRkZGRiIgc3RvcC1vcGFjaXR5PSIwLjA5ODAzOTIxNTY4NjI3NDUxIi8+CgkJPC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9Imdsb3NzLTMtZ3JhZGllbnQiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iMTg0My40MTI1IiB5MT0iMjQzOS44ODc1IiB4Mj0iMTkxMi43ODc1IiB5Mj0iMjM3MC41MTI1IiBzcHJlYWRNZXRob2Q9InBhZCI+CgkJCTxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiIHN0b3Atb3BhY2l0eT0iMC4yOTgwMzkyMTU2ODYyNzQ1Ii8+CgkJCTxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0ZGRkZGRiIgc3RvcC1vcGFjaXR5PSIwLjA5ODAzOTIxNTY4NjI3NDUxIi8+CgkJPC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImJvdHRvbS0yLWdyYWRpZW50IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjE3MjAuMiIgeTE9IjI0MTcuODUiIHgyPSIxNzIwLjIiIHkyPSIyMzY1LjY1IiBzcHJlYWRNZXRob2Q9InBhZCI+CgkJCTxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNCQ0JFQzAiLz4KCQkJPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjRTZFN0U4Ii8+CgkJPC9saW5lYXJHcmFkaWVudD48ZyBpZD0iYmFja2dyb3VuZCIgdHJhbnNmb3JtPSJtYXRyaXgoIDAuNDU1Nzk1Mjg4MDg1OTM3NSwgMCwgMCwgMC40NTU2ODg0NzY1NjI1LCAtNzcyLjE1LC0xMDc4KSAiPgoJCQk8cGF0aCBkPSIgTSAxOTEzLjUgMjM3NS4yIFEgMTkxMy41IDIzNzEuMjUgMTkxMC43IDIzNjguNCAxOTA3LjkgMjM2NS42IDE5MDMuOTUgMjM2NS42IEwgMTc0Ni4zIDIzNjUuNiAxNzI3LjY1IDIzOTkuMTUgMTY5NC4xIDI0MTcuODUgMTY5NC4xIDI1NzUuNDUgUSAxNjk0LjEgMjU3OS40NSAxNjk2LjkgMjU4Mi4yNSAxNjk5Ljc1IDI1ODUuMDUgMTcwMy43IDI1ODUuMDUgTCAxOTAzLjk1IDI1ODUuMDUgUSAxOTA3LjkgMjU4NS4wNSAxOTEwLjcgMjU4Mi4yNSAxOTEzLjUgMjU3OS40IDE5MTMuNSAyNTc1LjQ1IEwgMTkxMy41IDIzNzUuMiBaIi8+CgkJPC9nPjxtYXNrIGlkPSJtYXNrIj4KCQkJPHBhdGggZmlsbD0iI0ZGRkZGRiIgc3Ryb2tlPSJub25lIiBkPSIgTSA5OC43NSAxLjI1IFEgOTcuNDUgMCA5NS42NSAwIEwgMjMuOCAwIDE1LjMgMTUuMjUgMCAyMy44IDAgOTUuNiBRIDAgOTcuNDUgMS4zIDk4LjcgMi42IDEwMCA0LjQgMTAwIEwgOTUuNjUgMTAwIFEgOTcuNDUgMTAwIDk4Ljc1IDk4LjcgMTAwIDk3LjQgMTAwIDk1LjYgTCAxMDAgNC4zNSBRIDEwMCAyLjU1IDk4Ljc1IDEuMjUgWiIvPgoJCTwvbWFzaz48ZyBpZD0iZ2xvc3MtbGVmdCIgdHJhbnNmb3JtPSJtYXRyaXgoIDAuNDU1Nzk1Mjg4MDg1OTM3NSwgMCwgMCwgMC40NTU2ODg0NzY1NjI1LCAtNzcyLjE1LC0xMDc4KSI+CgkJCTxwYXRoIGZpbGw9InVybCgjZ2xvc3MtMS1ncmFkaWVudCkiIHN0cm9rZT0ibm9uZSIgZD0iIE0gMTgzMC4xNSAyMzY1LjYgTCAxNzQ2LjI1IDIzNjUuNiAxNjk0LjEgMjQxNy44IDE2OTQuMSAyNTA5Ljk1IDE4MzAuMTUgMjM2NS42IFoiLz4KCQk8L2c+PGcgaWQ9Imdsb3NzLXRvcCIgdHJhbnNmb3JtPSJtYXRyaXgoIDAuNDU1Nzk1Mjg4MDg1OTM3NSwgMCwgMCwgMC40NTU2ODg0NzY1NjI1LCAtNzcyLjE1LC0xMDc4KSI+CgkJCTxwYXRoIGZpbGw9InVybCgjZ2xvc3MtMi1ncmFkaWVudCkiIHN0cm9rZT0ibm9uZSIgZD0iIE0gMTkxMC43IDIzNjguNCBRIDE5MDcuOSAyMzY1LjYgMTkwMy45NSAyMzY1LjYgTCAxNzQ2LjMgMjM2NS42IDE3MjcuNjUgMjM5OS4xNSAxNjk0LjEgMjQxNy44NSAxNjk0LjEgMjQ3NS4zNSAxOTEzLjUgMjQ3NS4zNSAxOTEzLjUgMjM3NS4yIFEgMTkxMy41IDIzNzEuMjUgMTkxMC43IDIzNjguNCBaIi8+CgkJPC9nPjxnIGlkPSJnbG9zcy1yaWdodCIgdHJhbnNmb3JtPSJtYXRyaXgoIDAuNDU1Nzk1Mjg4MDg1OTM3NSwgMCwgMCwgMC40NTU2ODg0NzY1NjI1LCAtNzcyLjE1LC0xMDc4KSI+CgkJCTxwYXRoIGZpbGw9InVybCgjZ2xvc3MtMy1ncmFkaWVudCkiIHN0cm9rZT0ibm9uZSIgZD0iIE0gMTkxMC43IDIzNjguNCBRIDE5MDcuOSAyMzY1LjYgMTkwMy45NSAyMzY1LjYgTCAxNzc3LjQ1IDIzNjUuNiAxOTEzLjUgMjUwOS45NSAxOTEzLjUgMjM3NS4yIFEgMTkxMy41IDIzNzEuMjUgMTkxMC43IDIzNjguNCBaIi8+CgkJPC9nPjxnIGlkPSJib3R0b20tMSIgdHJhbnNmb3JtPSJtYXRyaXgoIDAuNDU1Nzk1Mjg4MDg1OTM3NSwgMCwgMCwgMC40NTU2ODg0NzY1NjI1LCAwLDApIj4KCQkJPHBhdGggZmlsbD0iIzAwMDAwMCIgZmlsbC1vcGFjaXR5PSIwLjI5ODAzOTIxNTY4NjI3NDUiIHN0cm9rZT0ibm9uZSIgZD0iIE0gMCA1Mi4yNSBMIDAgODMuNCA4My4zNSAwIDUyLjIgMCAzMS42IDMxLjY1IDAgNTIuMjUgWiIvPgoJCTwvZz48ZyBpZD0iYm90dG9tLTIiIHRyYW5zZm9ybT0ibWF0cml4KCAwLjQ1NTc5NTI4ODA4NTkzNzUsIDAsIDAsIDAuNDU1Njg4NDc2NTYyNSwgLTc3Mi4xNSwtMTA3OCkiPgoJCQk8cGF0aCBmaWxsPSJ1cmwoI2JvdHRvbS0yLWdyYWRpZW50KSIgc3Ryb2tlPSJub25lIiBkPSIgTSAxNzQzLjUgMjQxNS4wNSBRIDE3NDYuMyAyNDEyLjI1IDE3NDYuMyAyNDA4LjI1IEwgMTc0Ni4zIDIzNjUuNiAxNjk0LjEgMjQxNy44NSAxNzM2Ljc1IDI0MTcuODUgUSAxNzQwLjcgMjQxNy44NSAxNzQzLjUgMjQxNS4wNSBaIi8+CgkJPC9nPgoJCQkKCTxsaW5lYXJHcmFkaWVudCBpZD0iYmFja2dyb3VuZC1ncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB5Mj0iMSIgeDI9IjAiID4KCQk8c3RvcCBzdG9wLWNvbG9yPSIjODg4IiBvZmZzZXQ9IjAlIi8+CgkJPHN0b3Agc3RvcC1jb2xvcj0iIzAwMDAwMCIgb2Zmc2V0PSIxMDAlIi8+Cgk8L2xpbmVhckdyYWRpZW50PgoKCQkJCgkJCQoJCQk8ZyB0cmFuc2Zvcm09InNjYWxlKDMuMTI1KSB0cmFuc2xhdGUoMyAwKSIgaWQ9InBpY3R1cmUiPjxwYXRoIGQ9Ik03IDZINVYxYzAtLjYtLjQtMS0xLTFTMyAuNCAzIDF2NUgxYy0uNiAwLTEgLjQtMSAxdjZjMCAuNi40IDEgMSAxaDJ2MTdjMCAuNi40IDEgMSAxczEtLjQgMS0xVjE0aDJjLjYgMCAxLS40IDEtMVY3YzAtLjYtLjQtMS0xLTF6bS0xIDZIMlY4aDR2NHptMTAgN2gtMlYxYzAtLjYtLjQtMS0xLTFzLTEgLjQtMSAxdjE4aC0yYy0uNiAwLTEgLjQtMSAxdjZjMCAuNi40IDEgMSAxaDJ2NGMwIC42LjQgMSAxIDFzMS0uNCAxLTF2LTRoMmMuNiAwIDEtLjQgMS0xdi02YzAtLjYtLjQtMS0xLTF6bS0xIDZoLTR2LTRoNHY0em0xMC0xNWgtMlYxYzAtLjYtLjQtMS0xLTFzLTEgLjQtMSAxdjloLTJjLS42IDAtMSAuNC0xIDF2NmMwIC42LjQgMSAxIDFoMnYxM2MwIC42LjQgMSAxIDFzMS0uNCAxLTFWMThoMmMuNiAwIDEtLjQgMS0xdi02YzAtLjYtLjQtMS0xLTF6bS0xIDZoLTR2LTRoNHY0eiIvPjwvZz4KCQkJCgk8bGluZWFyR3JhZGllbnQgaWQ9InBpY3R1cmUtZ3JhZGllbnQiIHgxPSIwIiB5MT0iMCIgeTI9IjEiIHgyPSIwIiA+CgkJPHN0b3Agc3RvcC1jb2xvcj0iI2ZmZmZmZiIgb2Zmc2V0PSIwJSIvPgoJCTxzdG9wIHN0b3AtY29sb3I9IiNlNWVmZjkiIG9mZnNldD0iMTAwJSIvPgoJPC9saW5lYXJHcmFkaWVudD4KCgkJPC9kZWZzPgoKCQkKCgkJCTx1c2UgeGxpbms6aHJlZj0iI2JhY2tncm91bmQiIGZpbGw9InVybCgjYmFja2dyb3VuZC1ncmFkaWVudCkiIC8+CgoJCQoKCQkJPGcgbWFzaz0idXJsKCNtYXNrKSI+CgkJCQk8ZyB0cmFuc2Zvcm09IgoJCQkJICAgICAgICB0cmFuc2xhdGUoCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgNTAgNTAKKQogICAgICAgICAgICAgICAgICAgICAgICAgICAgdHJhbnNsYXRlKDAgMCkgIHNjYWxlKDAuNSkgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgdHJhbnNsYXRlKAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC01MCAtNTAKKSI+CgkJCQkJCTx1c2UgeGxpbms6aHJlZj0iI3BpY3R1cmUiIGZpbGw9InVybCgjcGljdHVyZS1ncmFkaWVudCkiICAvPgoJCQkJPC9nPgoJCQk8L2c+CgoJCTx1c2UgeGxpbms6aHJlZj0iI2JvdHRvbS0xIiAvPjx1c2UgeGxpbms6aHJlZj0iI2JvdHRvbS0yIiAvPgoKCQkJPHVzZSB4bGluazpocmVmPSIjZ2xvc3MtdG9wIiBvcGFjaXR5PSIxIiAvPgoKCgk8L3N2Zz4K
// @description  Parse the Faction Upgrades and Send to YATA
// @supportURL   https://www.torn.com/messages.php?p=compose&XID=1934501
// @updateURL    about:blank
// @author       Helcostr [1934501]
// @run-at       document-end
// @match        https://www.torn.com/factions.php?step=your*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      yata.alwaysdata.net
// ==/UserScript==

(function() {
    'use strict';
    // parse cookie
    const getCookie = (s)=>{
        let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
        return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
    };
    if (typeof $ != "function") {
        alert("JQuery Missing. This is a critical error.");
        return;
    }
    // Msgbox
    const msgbox = (msg)=>{
        $("#HCS_FacUpgr_Status").html(msg);
        $("#HCS_FacUpgr > div").removeClass("green red").addClass("blue");
    };

    // Response OK
    const valid = (msg)=>{
        msgbox("<b>" + msg +"</b>");
        $("#HCS_FacUpgr > div").removeClass("blue red").addClass("green");
    };

    // API Key
    const error_key = (msg,good)=>{
        let key = GM_getValue("key","");
        if (key == "") {
            key = "Insert API Key";
            msg = "No API Key stored";
            good = false;
        }
        if (good)
            msgbox("Here is your stored API key:");
        else
            msgbox("An error has occured: <b>"+msg+"</b>.<br>Please retype in your API key.");
        let input = $("<input id='api_key'>")
        if (good)
            input.val(key);
        else
            input.attr("placeholder",key);
        let button = $("<button>");
        button.text("Store");
        button.click(()=>{
            let key = $("#api_key").val();
            GM_setValue("key",key);
            if (!key_valid(key))
                return error_key("API Key is not the correct length.");
            msgbox("Your key has been stored. Ready to Submit.")
        });
        $("#HCS_FacUpgr_Status").append(input).append(button);
        if (good)
            $("#HCS_FacUpgr > div").removeClass("red green").addClass("blue");
        else
            $("#HCS_FacUpgr > div").removeClass("blue green").addClass("red");
    }
    const key_valid = (key)=>{
        return key.length == 16;
    };

    // Response Error
    const error = (msg)=>{
        msgbox("An error has occured: <b>" +msg+"</b>.<br>Please contact <a href='https://www.torn.com/profiles.php?XID=1934501'>Helcostr [1934501]</a> if you need help with this error message.");
        $("#HCS_FacUpgr > div").removeClass("blue green").addClass("red");
    };

    // Startup function
    const startup = ()=>{
        //Display box
        let infobox = '<div id="HCS_FacUpgr"><div class="info-msg-cont blue border-round m-top10 r2895"><div class="info-msg border-round"><i class="info-icon"></i><div class="delimiter"><div class="msg right-round"><p id="HCS_FacUpgr_Buttons"><a href="https://yata.alwaysdata.net/" target="_blank" style="float:right; margin-right: 5px; margin-top: 8px; font-weight: bold;">YATA</a></p><p id="HCS_FacUpgr_Status" style="margin-top: 10px;"></p></div></div></div></div><hr class="page-head-delimiter m-top10 m-bottom10 r2895"></div>';
        $(".content-title").after(infobox);

        //Set up buttons
        buttonSetup();
    };
    const buttonSetup = (buttonName,cb)=>{
        const buttonSetup = (text,cb)=>{
            let button = $('<button style="margin-right: 5px">');
            button.text(text);
            button.click(cb);
            $("#HCS_FacUpgr_Buttons").append(button);
        };
        $("#HCS_FacUpgr_Buttons").html("");
        if (typeof buttonName != "undefined")
            buttonSetup(buttonName,cb);
        buttonSetup("API Storage",()=>{error_key("",true)});
    }

    // Send to server
    const sendJSON = (json)=>{
        msgbox();
        let report = json;
        let key = GM_getValue("key","");
        if (key.length != 16) {
            error_key("Please insert your API key");
            return;
        }
        GM_xmlhttpRequest({
            method: "POST",
            url: "https://yata.alwaysdata.net/chain/importUpgrades/",
            data: JSON.stringify(report),
            headers: {
                "key":key
            },
            onload: resp=> {
                try {
                    let obj = JSON.parse(resp.responseText);
                    if ("message" in obj) {
                        if ("type" in obj && obj.type>0)
                            valid(obj.message);
                        else if (obj.type == -1) {
                            switch(obj.message.apiErrorCode) {
                                case 1:
                                case 2:
                                case 10:
                                    error_key(obj.message.apiError);
                                    break;
                                default:
                                    error(obj.message.apiError);
                            }
                        } else
                            error(obj.message);
                    } else if (obj.status == 200)
                        error("Everything seems to be ok???");
                    else
                        error("No message received from the server");
                } catch (e) {
                    error("Failed to parse response from server");
                }
            },
            ontimeout: ()=>{
                error("Request has timed out");
            },
            onerror: ()=>{
                error("Unknown error has occured when trying to send the data");
            },
            onabort: ()=>{
                error("Upon sending the data, the request was canceled");
            }
        });
    };
    $(document).ajaxComplete((event,xhr,settings)=>{
        if (settings.url.search("factions.php") != -1 && $(".contributions-list").length !== 0) {
            let data = JSON.parse(xhr.responseText);
            let name = data.contributors[0][0].challenge;
            let contributors = [];
            data.contributors.forEach(e=>Object.keys(e).forEach(f=>contributors[f] = {exmember:e[f].exmember,playername:e[f].playername,total:parseInt(e[f].total.replace(/,/g, '')),userid:parseInt(e[f].userid)}));
            let report = {
                author:parseInt(getCookie("uid")),
                type:data.upgrade.type,
                name: name,
                contributors:contributors
            };
            buttonSetup("Send "+ name+ " to YATA",()=>{sendJSON(report)});
        }
    });
    startup();
})();
