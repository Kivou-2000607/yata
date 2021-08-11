$(document).on('click', '#yata-login-submit', function(e){
    e.preventDefault();

    // WARNING: IT IS NOT TOLERATED TO MODIFY THIS FUNCTION
    // as it will remove the warning when users enter their API key on non official instances of YATA.
    // Changing it will be seen as making your instance of YATA looks official, thus raising suspicions.
    if (window.location.host != "yata.yt") {
      var c = confirm("This is not the official YATA website which is hosted on https://yata.yt.\nWhere it is allowed to host instances of YATA on personal servers, make sure you know who's hosting it and that they have no malicious intents.\n\nKivou [2000607]");
      if (c == false) {
          return
      }
    }

    $("#header").load( "/login", {
        key: $("#yata-login-key").val(),
        csrfmiddlewaretoken:  getCookie("csrftoken"),
    });
    $(this).html(spinner);
});

$(document).on('click', '#yata-logout-submit', function(e){
    $(this).html(spinner);
});

$(document).on('click', '#yata-delete-submit', function(e){
    var r = confirm("Are you sure you want to delete your account? All data will be removed from the database.");
    if (r == false) {
        e.preventDefault();
    }
});

$(document).on('click', '#yata-toggle-color-mode', function(e){
  e.preventDefault();

  $(this).parent("div").parent("div").load( "/update_session", {
      key: "dark",
      csrfmiddlewaretoken:  getCookie("csrftoken"),
  });

  // need to workout how to reload the CSS dynamically knowing that
  // in production the filename is not known (whitenoise)

});

const spinner = '<i class="fas fa-spinner fa-pulse"></i>';

function toggle_h(h) {
    var d = h.next("div");
    var i = h.find("i[class^='fas fa-caret']");

    // close all other sections
    const lookup = h.is("h3") ? ["div.module", "h3.module-doc"] : ["div.module-doc", "h4.command-doc"]
    h.closest(lookup[0]).find(lookup[1]).each((i, item) => {
        if(item != h[0]) {
            $(item).next("div").slideUp("fast");
            $(item).find("i[class^='fas fa-caret']").removeClass("fa-rotate-90");
        }
    });

    // toggle
    d.slideToggle("fast", function(){
        if (d.css("display") == "none") {
            i.removeClass("fa-rotate-90");
        } else {
            i.addClass("fa-rotate-90");
        }
    });
}

// show/hide command
$(document).on('click', 'h3.module-doc, h4.command-doc', function(e){
    e.preventDefault();
    // get h2 and div
    var h = $(this);
    toggle_h(h);
});

function fancyCountdown(time)
{   // From https://stackoverflow.com/a/11486026
    // days:hours:minutes:seconds
    var days = ~~(time / 86400);
    var hrs = ~~((time % 86400) / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;

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

function fancyTimeFormat(time)
{   // From https://stackoverflow.com/a/11486026
    // Hours:minutes:seconds
    var hrs = ~~(time / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;

    var ret = "";

    if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    }

    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

const nav = (url) =>{
     console.log("nav" + url);
     window.history.pushState(null, document.title, url);
};

// const nav = (r,s,x,url) =>{
//     console.log(r);
//     console.log(s);
//     console.log(x);
//     console.log(url);
//     window.history.pushState(r, document.title, url);
// };

// parse cookie
const getCookie = (s)=>{
    let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
    return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
};


// header navigation
$(document).on('click', 'div.yt-main-link a', e => {
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(spinner+'&nbsp;Loading '+$(e.currentTarget).attr("title"))
    $(e.currentTarget).find("i").replaceWith(spinner);
});

// sub header navigation
$(document).on('click', 'div.yt-cat-link', e=>{
    e.preventDefault();
    var link = $(e.currentTarget).children("a")
    $( "#content-update" ).load( link.attr("href"), {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(link.attr("href")));
    $("#content-update h2").addClass("grey").addClass("px-2").html('<div class="ps-2">'+spinner+'&nbsp;Loading '+link.attr("title")+'</div>')
    $("div.error").hide();
});


// pagination nav
$(document).on('click', 'a.yt-page-link', function(e){
    e.preventDefault();
    var reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( $(e.currentTarget).attr("href"), function() {});
    $(e.currentTarget).closest("table").find("tr").html('<td colspan="*" class="text-center">'+spinner+'</td>');
});

// prevent show/hide
$(document).on('click', 'h2.title.toggle-display div.no-click', function(e){
  var h = $(this).closest("h2");
  var div = h.next("div");
  var i = h.find("div.toggle-rotate").find("i");
  if(div.css("display") == "none") {
      h.removeClass("rounded").removeClass("mb-3");
      i.addClass("fa-rotate-90");
  } else {
    e.stopPropagation()
  }
});

// show/hide module
$(document).on('click', 'h2.title.toggle-display', function(e){
    e.preventDefault();
    var h = $(this).closest("h2");
    if (!($(e.target).hasClass("update-type") && !h.hasClass("rounded"))) {
        var i = h.find("div.toggle-rotate").find("i");
        var div = h.next("div");
        if(div.css("display") == "none") {
            h.removeClass("rounded").removeClass("mb-3");
            i.addClass("fa-rotate-90");
        }
        div.slideToggle("fast", function(){
            if(div.css("display") == "none") {
                h.addClass("rounded").addClass("mb-3");
                i.removeClass("fa-rotate-90");
            }
        });
    }
});

// refresh loot timer
window.setInterval(function(){
    $("span#loot-countdown-header").each(function() {
        const loot = parseInt($.trim($(this).attr("data-lts")));
        const name = $.trim($(this).attr("data-nam"));
        const tid = $.trim($(this).attr("data-tid"));
        const now = parseInt(Date.now() / 1000);
        const diff = loot-now;

        let cd = fancyTimeFormat(diff);
        let cl = ""

        if(diff < 60) {
            cd = "now"
        }

        if (diff < 60*5) {
            cl = "error"
        } else if(diff < 60*15) {
            cl = "warning"
        }

        $(this).html('<a class="'+cl+'" href="https://www.torn.com/loader.php?sid=attack&user2ID='+tid+'" target="_blank">'+name+': '+cd+'</a>');

    });
}, 1000);

//
// $(document).on('click', '.overlay.close', function(e){
//     e.preventDefault();
//     $(this).parent("div.container").css("display", "none");
// });
//
// $(document).on('click', '.close-button', function(e){
//     e.preventDefault();
//     $(this).closest("div.container").css("display", "none");
// });
//

// full width
$(document).on('click', '.yt-full-width', function(e) {
  e.preventDefault();
  $("#main-content").css("max-width", "100%");
  $(this).closest("li").hide();

});
