// delete wall
$(document).on('click', '.wall-delete', function(e){
    e.preventDefault();
    var wallId = $(e.currentTarget).closest("td").attr("data-val");
    $(e.currentTarget).closest("tr").load( "/faction/walls/manage/", {
        type:"delete", wallId: wallId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// toggle wall from list
$(document).on('click', '.wall-toggle', e=>{
    e.preventDefault();
    var td = $(e.currentTarget).closest("td");
    var wallId = td.attr("data-val");
    td.load( "/faction/walls/manage/", {
        type:"toggle", wallId: wallId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});


// create report
$(document).on('click', '.wall-report-add', e=>{
    e.preventDefault();
    var wallId = $(e.currentTarget).closest("td").attr("data-val");
    console.log(wallId);
    $( "#content-update" ).load( "/faction/attacks/", {
        type: "new", wallId: wallId,
        csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating report ');
});

// see report
$(document).on('click', '.wall-report-see', e=>{
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    console.log(reportId);
    $("#content-update").load( "/faction/attacks/" + reportId, {
        reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Loading report');
    $("div.error").hide();
});
