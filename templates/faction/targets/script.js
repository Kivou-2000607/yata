function fancyTimeFormat(time)
{   // From https://stackoverflow.com/a/11486026
    // Hours, minutes and seconds
    var hrs = ~~(time / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    }

    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

// refresh target from target list by clicking on the row
$(document).on('click', 'tr[id^="target-list-refresh-"] > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var reload = $(this).closest("tr");
    // var targetId = reload.attr("id").split("-").pop();
    var targetId = reload.attr("data-val");
    reload.removeClass("old-refresh");
    reload.load( "/faction/target/", {
        targetId: targetId,
        type: "update",
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.html('<td colspan="7" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
});

// delete target from target list button
$(document).on('click', 'a.target-list-delete', function(e){
    e.preventDefault();
    var reload = $(this).closest("tr");
    var targetId = reload.attr("data-val");
    reload.load( "/faction/target/", {
        targetId: targetId,
        type: "delete",
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.remove();
});

// refresh timer target update
window.setInterval(function(){
    $(".update-timer").each(function() {
        var tr = $(this).closest("tr");
        var status = tr.find(".status");

        var tsRefresh = parseInt($.trim($(this).attr("data-val")));
        var tsStatus = parseInt($.trim(status.attr("data-val")));
        var tsNow = parseInt(Date.now() / 1000)

        // transform notations if > 2 hours
        if ( tsNow - tsRefresh > 7200 ) {
            $(this).html("> 2 hrs");
            tr.addClass("old-refresh");
            $(this).removeClass('need-refresh');
            status.removeClass('need-refresh');
        } else {

            // add/remove flash if tsStatus < tsRefresh
            if (tsStatus && tsRefresh) {
                if(tsStatus < tsNow) {
                    statusStr = "Out since " + fancyTimeFormat(tsNow - tsStatus) + " s"
                    status.addClass('need-refresh');
                    $(this).addClass('need-refresh');
                } else {
                    status.removeClass('need-refresh');
                    $(this).removeClass('need-refresh');
                    statusStr = status.text().substring(0, 6);
                    statusStr += fancyTimeFormat(tsStatus - tsNow)
                }
                // update hosp time
                status.html(statusStr)
            }
            $(this).html(fancyTimeFormat(tsNow - tsRefresh))
        }

    });
}, 1000);
