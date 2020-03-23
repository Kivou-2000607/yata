/* chain list */

// combined report
$(document).on('click', '#faction-chain-combined', e=>{
    e.preventDefault();
    $("#content-update").load( "/faction/chains/combined/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav("/faction/chains/combined/"));
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading combined report');
    $("div.error").hide();
});

/* chain list button */

// create report
$(document).on('click', '.faction-chains-create', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).attr("data-val");
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/chains/manage/", {
        type: "create", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// create report
$(document).on('click', '.faction-chains-cooldown', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).attr("data-val");
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/chains/manage/", {
        type: "cooldown", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
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

    var chainId = $(e.currentTarget).attr("data-val");
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/chains/manage/", {
        type: "delete", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// toggle combine report
$(document).on('click', '.faction-chains-combine', e=>{
    e.preventDefault();
    // handle n combined
    var n = parseInt($("#n-combined").text());
    if($(e.currentTarget).children("i").hasClass("fa-toggle-off")) {
        n += 1;
    } else {
        n -= 1;
    }
    $("#n-combined").html(n);

    // handle toggle
    var chainId = $(e.currentTarget).attr("data-val");
    var td = $(e.currentTarget).parents("td");
    td.load( "/faction/chains/manage/", {
        type: "combine", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// see report
$(document).on('click', '.faction-chains-see', e=>{
    e.preventDefault();
    var chainId = $(e.currentTarget).attr("data-val");
    $("#content-update").load( "/faction/chains/" + chainId, {
        chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav("/faction/chains/" + chainId));
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
    $("#individal-report-"+memberId).load( "/faction/chains/individual/", {
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


// share reports
$(document).on('click', '#faction-chain-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("span")
    var chainId = $(e.currentTarget).attr("data-val");
    span.load( "/faction/chains/manage/", {
        type: "share", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<span style="margin-left: 5px; width: '+span.width()+'px">' + spinner + '</span>');
});
$(document).on('click', '#faction-attacks-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("span")
    var reportId = $(e.currentTarget).attr("data-val");
    console.log(reportId);
    span.load( "/faction/attacks/manage/", {
        type: "share", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<span style="margin-left: 5px; width: '+span.width()+'px">' + spinner + '</span>');
});
$(document).on('click', '#faction-revives-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("span")
    var reportId = $(e.currentTarget).attr("data-val");
    console.log(reportId);
    span.load( "/faction/revives/manage/", {
        type: "share", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<span style="margin-left: 5px; width: '+span.width()+'px">' + spinner + '</span>');
});
