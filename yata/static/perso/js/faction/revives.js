$(document).on('change', '#date-live-revives', e=>{
    e.preventDefault();
    var start = parseInt($("#ts-start-revives").val());
    var end = parseInt($("#ts-end-revives").val());
    var live = $(e.currentTarget).prop('checked');
    if(live) {
        $("#date-end-revives").addClass("valid").removeClass("error").html("Will be constantly udpated");
        if(start) {
            $("#create-report-revives").show();
        } else {
            $("#create-report-revives").hide();
        }
    } else {
        $("#date-end-revives").removeClass("valid").addClass("error").html('<i class="fas fa-plus-circle"></i>&nbsp;&nbsp;Add an ending date (or leave blank for live)');
        $("#create-report-revives").hide();
    }
});

// create report
$(document).on('click', '#create-report-revives', e=>{
    e.preventDefault();
    var start = parseInt($("#ts-start-revives").val());
    var end = parseInt($("#ts-end-revives").val());
    if($("#date-live-revives").prop('checked')) {
        var live = 1;
        var end = 0;
    } else {
        var live = 0
    }
    $( "#content-update" ).load( "/faction/revives/", {
        start: start, end: end, live: live, type: "new",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating report ');
});

// delete report
$(document).on('click', '.faction-revives-reports-delete', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $(e.currentTarget).closest("tr").load( "/faction/revives/manage/", {
        type:"delete", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// see report
$(document).on('click', '.faction-revives-reports-see', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $("#content-update").load( "/faction/revives/" + reportId, {
        reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav("/faction/revives/" + reportId));
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading report');
    $("div.error").hide();
});

// show hide
$(document).on('click', '.faction-revives-report-toggle', e=>{
    e.preventDefault();
    var splt = e.currentTarget.id.split("-");
    var factionId = $(e.currentTarget).attr("data-val");
    var order = splt.pop();
    var page = splt.pop();
    var reportId = splt.pop();
    var reload = $(e.currentTarget).closest("td");
    $( "#content-update" ).load( "/faction/revives/" + reportId, {
        reportId: reportId, factionId: factionId, type: "toggle", o_pl: order, page: page,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Reload report ');
});

// show hide
$(document).on('click', '#faction-revives-report-update', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $( "#content-update" ).load( "/faction/revives/" + reportId, {
        reportId: reportId, update: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Recompute report ');
});

// filters
$(document).on('click', 'span[id^="faction-revives-report-"]', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    var type = e.currentTarget.id.split("-").pop();
    $( "#content-update" ).load( "/faction/revives/" + reportId, {
        reportId: reportId, type: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Recompute report ');
});

$(document).on('click', 'form.revives > i.filter-player,form.revives > i.filter-player-activated', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).attr("data-val").split("-")
    var reportId = splt[0];
    var playerId = splt[1];
    var reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( "/faction/revives/list/" + reportId, {
        playerId: playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html('<td>'+spinner+'</td>');
});

$(document).on('change', 'select.faction-revive-header-filter', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).val().split("-");
    var reportId = splt[0];
    var playerId = splt[1];
    var reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( "/faction/revives/list/" + reportId, {
        playerId: playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html('<td>'+spinner+'</td>');
});
