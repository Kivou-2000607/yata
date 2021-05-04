
// countdown
window.setInterval(function(){
    $(".event-countdown").each(function() {
        var date = parseInt($.trim($(this).attr("data-val")));
        var now = parseInt(Date.now() / 1000)
        var countdown = Math.max(date - now, 0)

        // transform notations if < 0
        if ( countdown  == 0 ) {
            $(this).addClass("valid");
            $(this).html("Started");
        } else if ( countdown < 3600 ) {
            $(this).addClass("error");
            $(this).closest("div.faction-event").addClass("faction-event-urgent");
            $(this).html(fancyCountdown(countdown))
        } else if ( countdown  < 24*3600 ) {
            $(this).addClass("warning");
            $(this).html(fancyCountdown(countdown))
            $(this).closest("div.faction-event").addClass("faction-event-soon");
        } else {
            $(this).addClass("neutral");
            $(this).html(fancyCountdown(countdown))
        }

    });
}, 1000);


// share reports
$(document).on('click', '#faction-chain-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("div")
    var chainId = $(e.currentTarget).attr("data-val");
    span.load( "/faction/chains/manage/", {
        type: "share", chainId: chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});
$(document).on('click', '#faction-attacks-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("div")
    var reportId = $(e.currentTarget).attr("data-val");
    span.load( "/faction/attacks/manage/", {
        type: "share", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<span style="margin-left: 5px; width: '+span.width()+'px">' + spinner + '</span>');
});
$(document).on('click', '#faction-revives-report-share', e=>{
    e.preventDefault();
    var span = $(e.currentTarget).closest("div")
    var reportId = $(e.currentTarget).attr("data-val");
    span.load( "/faction/revives/manage/", {
        type: "share", reportId: reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<span style="margin-left: 5px; width: '+span.width()+'px">' + spinner + '</span>');
});
