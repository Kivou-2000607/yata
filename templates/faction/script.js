function fancyCountdown(time)
{   // From https://stackoverflow.com/a/11486026
    // days, hours, minutes and seconds
    var days = ~~(time / 86400);
    var hrs = ~~((time % 86400) / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;
    console.log(days, hrs, mins, secs);

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (days > 0) {
        ret += "" + days + " day" + (days != 1 ? "s " : " ");
    }

    ret += (hrs < 10 ? "0" : "")
    ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

// update history on load
const afterLoad = (r,s,x) =>{
    window.history.pushState(null, document.title, x.url);
};

// parse cookie
const getCookie = (s)=>{
    let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
    return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
};

// nav links
$(document).on('click', 'table.faction-categories td', e=>{
    e.preventDefault();
    var l = $(e.currentTarget).children("a").attr("href").split("/")[2];
    $( "#content-update" ).load( "/faction/"+l+"/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    },afterLoad);
    $("#content-update h2").addClass("grey").html(spinner+'&nbsp;&nbsp;Loading '+l)
    $("div.error").hide();
});


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
