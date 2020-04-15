// refresh target from target list by clicking on the row
$(document).on('click', 'tr[id^="target-list-refresh-"] > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var reload = $(this).closest("tr");
    // var targetId = reload.attr("id").split("-").pop();
    var targetId = reload.attr("data-val");
    reload.removeClass("old-refresh");
    reload.load( "/target/target/", {
        targetId: targetId,
        type: "update",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<td colspan="14" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
});

// toggle faction target
$(document).on('click', 'a.target-list-faction', function(e){
    e.preventDefault();
    var targetId = $(this).attr("id").split("-").pop();
    var reload = $(this).closest("td");
    reload.load( "/faction/target/", {
        targetId: targetId,
        type: "toggle",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<i class="fas fa-spinner fa-pulse"></i>');
});

// delete target from target list button
$(document).on('click', 'a.target-list-delete', function(e){
    e.preventDefault();
    var targetId = $(this).attr("id").split("-").pop();
    var reload = $("#target-list-refresh-"+targetId);
    reload.load( "/target/target/", {
        targetId: targetId,
        type: "delete",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.remove();
});

// edit note
$(document).on('focusout', 'input.target-list-note', function(e){
    e.preventDefault();
    var targetId = $(this).next("input").attr("value");
    var note = $(this).val();
    var reload = $(this).closest('td');
    // alert(targetId+notes)
    reload.load( "/target/target/", {
        targetId: targetId,
        note: note,
        type: "note",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<i class="fas fa-spinner fa-pulse" style="margin-top: 8px"></i>');
});


// refresh all targets from target list by clicking on title refresh button
$(document).on('click', '#target-refresh', function(e){
    e.preventDefault();
    var i = 1;
    $("#target-targets").find('tr[id^="target-list-refresh-"]').each(function() {
        var reload = $(this);
        var targetId = reload.attr("id").split("-").pop();
        var wait = i*500 + parseInt(i/10)*3000;
        (function(index) {
            setTimeout(function() {
                reload.load( "/target/target/", {
                    targetId: targetId,
                    type: "update",
                    csrfmiddlewaretoken: getCookie("csrftoken")
                });
                reload.removeClass('old-refresh');
                reload.html('<td colspan="13" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
             }, wait);
        })(i);
        i++;
    });
});

// add target manually
$(document).on('click', '#target-add-submit', function(e){
    e.preventDefault();
    var id = $("#target-add-id").val();
    $( "#content-update" ).load( "/target/target/", {
        targetId: id,
        type: "addById",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html('<i class="fas fa-spinner fa-pulse"></i>&nbsp;&nbsp;Adding target id '+id+' (1 API call)')

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
