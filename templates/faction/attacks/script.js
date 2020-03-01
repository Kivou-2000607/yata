$(document).on('change', '#date-live', e=>{
    e.preventDefault();
    var start = parseInt($("#ts-start").val());
    var end = parseInt($("#ts-end").val());
    var live = $(e.currentTarget).prop('checked');
    if(live) {
        $("#date-end").addClass("valid").removeClass("error").html("Will be constantly udpated");
        if(start) {
            $("#create-report").show();
        } else {
            $("#create-report").hide();
        }
    } else {
        $("#date-end").removeClass("valid").addClass("error").html('<i class="fas fa-plus-circle"></i>&nbsp;&nbsp;Add an ending date (or leave blank for live)');
        $("#create-report").hide();
    }
});

// create report
$(document).on('click', '#create-report', e=>{
    e.preventDefault();
    var start = parseInt($("#ts-start").val());
    var end = parseInt($("#ts-end").val());
    if($("#date-live").prop('checked')) {
        var live = 1;
        var end = 0;
    } else {
        var live = 0
    }
    $( "#content-update" ).load( "/faction/attacks/", {
        start: start, end: end, live: live, type: "new",
        csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating report ');
});

// delete report
$(document).on('click', '.faction-attacks-reports-delete', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $(e.currentTarget).closest("tr").load( "/faction/attacks/manage/", {
        type:"delete", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// see report
$(document).on('click', '.faction-attacks-reports-see', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $("#content-update").load( "/faction/attacks/" + reportId, {
        reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading report');
    $("div.error").hide();
});


// show hide
$(document).on('click', '.faction-attacks-report-toggle', e=>{
    e.preventDefault();
    var splt = e.currentTarget.id.split("-");
    var factionId = $(e.currentTarget).attr("data-val");
    var page = splt.pop();
    var reportId = splt.pop();
    var type = splt.pop();
    var reload = $(e.currentTarget).closest("td");
    console.log(factionId, reportId, type);
    $( "#content-update" ).load( "/faction/attacks/" + reportId, {
        reportId: reportId, factionId: factionId, type: type, page: page,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Reload report ');
});

// show hide
$(document).on('click', '#faction-attacks-report-update', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $( "#content-update" ).load( "/faction/attacks/" + reportId, {
        reportId: reportId, update: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Recompute report ');
});
