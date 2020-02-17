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
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.html('<td colspan="13" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
});

// delete target from target list button
$(document).on('click', 'a.target-list-delete', function(e){
    e.preventDefault();
    var targetId = $(this).attr("id").split("-").pop();
    var reload = $("#target-list-refresh-"+targetId);
    reload.load( "/target/target/", {
        targetId: targetId,
        type: "delete",
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
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
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
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
                    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
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
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
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

        // add/remove flash if tsStatus < tsRefresh
        if (tsStatus) {
            if(tsStatus < tsNow) {
                statusStr = "OUT"
                status.addClass('need-refresh');
                $(this).addClass('need-refresh');
            } else {
                status.removeClass('need-refresh');
                $(this).removeClass('need-refresh');

                statusStr = status.text().substring(0, 6);

                // update hosp time
                sStatus = tsStatus - tsNow
                mStatus = Math.floor(sStatus / 60);
                sStatus = sStatus % 60;
                if (mStatus) {
                    spad = ("0"+sStatus.toString()).slice(-2);
                    statusStr += mStatus.toString()+" mins "+spad+" s"
                } else {
                    statusStr += sStatus.toString()+" s"
                }

            }

            // update hosp time
            status.text(statusStr)
        }

        // transform notations if > 2 hours
        if ( tsNow - tsRefresh > 7199 ) {
            $(this).html("> 2 hrs");
            tr.addClass("old-refresh");
        } else {
            sRefresh = tsNow - tsRefresh
            mRefresh = Math.floor(sRefresh / 60);
            sRefresh = sRefresh % 60;
            if (mRefresh) {
                spad = ("0"+sRefresh.toString()).slice(-2);
                $(this).html(mRefresh.toString()+" mins "+spad+" s");
            } else {
                $(this).html(sRefresh.toString()+" s");
            }
        }

    });
}, 1000);
