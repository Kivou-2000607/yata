/* chain list */

// combined report
$(document).on('click', '#faction-chain-combined', e=>{
    e.preventDefault();
    $("#content-update").load( "/faction/combined/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading combined report');
    $("div.error").hide();
});

/* chain list button */

// create report
$(document).on('click', '.faction-chains-create', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).siblings("input.faction-chain-id").val();
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/report/manage/", {
        type: "create", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad).html(spinner);
});

// create report
$(document).on('click', '.faction-chains-cooldown', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).siblings("input.faction-chain-id").val();
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/report/manage/", {
        type: "cooldown", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad).html(spinner);
});

// delete report
$(document).on('click', '.faction-chains-delete', e=>{
    e.preventDefault();
    // handle n combined
    var n = parseInt($("#n-combined").text());
    if ($(e.currentTarget).siblings("a").children("i").hasClass("fa-toggle-on")) {
        n -= 1;
    }
    $("#n-combined").html(n);

    var chainId = $(e.currentTarget).siblings("input.faction-chain-id").val();
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/report/manage/", {
        type: "delete", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad).html(spinner);
});

// toggle combine report
$(document).on('click', '.faction-chains-combine', e=>{
    console.log("YATA: Hello, you pushed toggle");
    e.preventDefault();
    console.log("YATA: you passed prevet default");
    // handle n combined
    var n = parseInt($("#n-combined").text());
    console.log("YATA: you parsed n:" + n);
    if($(e.currentTarget).children("i").hasClass("fa-toggle-off")) {
        console.log("YATA: n+1:" + n);
        n += 1;
        console.log("YATA: n+1:" + n);
    } else {
        console.log("YATA: n-1:" + n);
        n -= 1;
        console.log("YATA: n-1:" + n);
    }
    console.log("YATA: before getting combined");
    $("#n-combined").html(n);
    console.log("YATA: after getting combined");

    // handle toggle
    var chainId = $(e.currentTarget).siblings("input.faction-chain-id").val();
    console.log("YATA: chain id"+chainId);
    var td = $(e.currentTarget).parents("td");
    console.log("YATA: chain td");
    console.log(td);
    td.load( "/faction/report/manage/", {
        type: "combine", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad).html(spinner);
    console.log("YATA: and now we are after sending the request");
});

// see report
$(document).on('click', '.faction-chains-see', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).siblings("input.faction-chain-id").val();
    $("#content-update").load( "/faction/report/" + chainId, {
        chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading report');
    $("div.error").hide();
});

/* reports */

// toggle zero-hits
$(document).on('click', '#toggle-zero-hits', e=>{
    e.preventDefault();
    $(".zero-hits").slideToggle('fast').promise().done(()=>{
        $("#zero-hits-icon").toggleClass("fa-toggle-on fa-toggle-off");
    });
});

// toggle non-members
$(document).on('click', '#toggle-kicked-members', e=>{
    e.preventDefault();
    $(".kicked-members").slideToggle('fast').promise().done(()=>{
        $("#kicked-members-icon").toggleClass("fa-toggle-on fa-toggle-off");
    });
});

// show individual report
$(document).on('click', 'tr[id^="faction-ireport-"] > td:not(.dont-touch-me)', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).closest("tr").attr("id").split("-");
    var memberId = splt.pop();
    var chainId = splt.pop();
    if( !$( "#individal-report-"+memberId ).length ) {
        $('<tr id="individal-report-'+memberId+'"></tr>').insertAfter($(e.currentTarget).closest('tr'));
    }
    $("#individal-report-"+memberId).load( "/faction/report/individual/", {
        chainId: chainId,
        memberId: memberId,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="12" style="text-align: center;">'+spinner+'</td>');
});

// close individual report
$(document).on('click', '[id^="individal-report-"]', e=>{
    e.preventDefault();
    $(e.currentTarget).html("");
});
