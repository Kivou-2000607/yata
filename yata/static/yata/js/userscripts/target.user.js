// ==UserScript==
// @name         Yata Target Import
// @version      0.1
// @description  Import target to yata from a profile page
// @updateURL    about:blank
// @author       SVD_NL
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
            .click( () => sendTarget());
        let targetDetailsButton = $("<button class='YATA-button'>")
            .text("Target details")
            .click( () => addOptionBox());
        let apiButton = $("<button class='YATA-button'>")
            .text("API Key")
            .click( () => errorKey("",true));
        $("#YATA-message-buttons")
            .append(addButton)
            .append(targetDetailsButton)
            .append(apiButton);
    }

    function addOptionBox() {
        let optionBox = $("<div id=YAYA-target-option-box class='YATA-messagebox'></div>");
        let noteInput = $("<input id='YATA-target-note' class='YATA-input' placeholder='Enter note'>");
        let colorPicker = $("<select id='YATA-target-color' class='YATA-select'></select>")
            .append("<option value=0>Black</option>")
            .append("<option value=1>Green</option>")
            .append("<option value=2>Yellow</option>")
            .append("<option value=3>Red</option>");
        optionBox
            .append(noteInput)
            .append(colorPicker);
        
        $("#YATA-infobox").append(optionBox);
    }

    function sendTarget() {
        let payload = constructJSON();
        GM_xmlhttpRequest({
            method: "POST",
            url: yataTargetUrl,
            data: JSON.stringify(payload),
            onload: response => {alert(response.responseText)}
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