// ==UserScript==
// @name         Yata Target Import
// @version      0.2
// @description  Import target to yata from a profile page
// @downloadURL  https://github.com/Kivou-2000607/yata/tree/99-script-to-importexport-target-from-profile/yata/static/yata/js/userscripts/target.user.js
// @updateURL    https://github.com/Kivou-2000607/yata/tree/99-script-to-importexport-target-from-profile/yata/static/yata/js/userscripts/target.user.js
// @author       SVD_NL [2363978]
// @run-at       document-end
// @match        https://www.torn.com/profiles.php?XID=*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// @grant        GM_getResourceText
// @connect      yata.yt
// @require      https://yata.yt/static/yata/js/userscripts.js
// @resource     YATA_CSS https://yata.yt/static/yata/css/userscripts.css
// ==/UserScript==

(function() {
    'use strict';

    const cssTxt = GM_getResourceText("YATA_CSS");
    GM_addStyle(cssTxt);
    //Included in CSS if accepted
    GM_addStyle("select.YATA-select {display: inline;height: 22px;margin: 4px;border: 0;color: #666;background-color: #fff;border-radius: 4px;text-align: center;}")

    const yataTargetUrl = "https://yata.yt/api/v1/targets/import/";
    
    function main() {
        addInfoBox();
    }

    function addInfoBox() {
        $("#profileroot").before(infobox);
        let addButton = $("<button class='YATA-button'>")
            .text("Add to target list")
            .click( () => addOptionBox());
        let apiButton = $("<button class='YATA-button'>")
            .text("API Key")
            .click( () => errorKey("",true));
        $("#YATA-message-buttons")
            .append(addButton)
            .append(apiButton);
    }

    function addOptionBox() {
        if ($("#YATA-target-option-box").length) {
            $("#YATA-target-option-box").toggle();
            return;
        }
        let optionBox = $("<div id=YATA-target-option-box class='yata-messagebox'></div>");
        let noteInput = $("<input id='YATA-target-note' class='YATA-input' placeholder='Enter note'>");
        let colorPicker = $("<select id='YATA-target-color' class='YATA-select'></select>")
            .append("<option value=0>Black</option>")
            .append("<option value=1>Green</option>")
            .append("<option value=2>Yellow</option>")
            .append("<option value=3>Red</option>");
        let importButton = $("<button class='YATA-button'>")
            .text("Add Target")
            .click( () => sendTarget());
        optionBox
            .append(noteInput)
            .append(colorPicker)
            .append(importButton);
        
        $("#YATA-infobox").append(optionBox);
    }

    function sendTarget() {
        let payload = constructJSON();
        GM_xmlhttpRequest({
            method: "POST",
            url: yataTargetUrl,
            data: JSON.stringify(payload),
            onload: resp => {
                try {
                    const obj = JSON.parse(resp.responseText);
                    console.log(resp.status);
                    console.log(obj);
                    if (resp.status === 400) {
                        if (obj.error.code === 4) error(`API error (${obj.error.error})`);
                        else error(`User error (${obj.error.error})`);
                    }
                    else if (resp.status === 500) error("Server error (" + obj.error.error + ")");
                    else if (resp.status === 200) valid(obj.message);
                    else error("No message received from the server");
                } catch (e) {
                    error("Failed to parse response from server" + e);
                }
            },
            ontimeout: () => {
                error("Request has timed out");
            },
            onerror: () => {
                error("Unknown error has occured when trying to send the data");
            },
            onabort: () => {
                error("Upon sending the data, the request was canceled");
            }
        });
    }

    function constructJSON() {
        let key = GM_getValue("key","");
        let note = $("#YATA-target-note").val();
        if (!note) {
            note = "";
        }
        let color = $("#YATA-target-color").val();
        if (!color) {
            color = 0;
        }

        let url = window.location.href;
        let idRegEx = /(?<=XID=)\d{1,7}/g;
        let userId = idRegEx.exec(url);

        const payload = {};
        payload.key = key;
        payload.targets = {};
        payload.targets[userId] = {note: note, color: color}
        
        return payload;
    }

    main();
})();