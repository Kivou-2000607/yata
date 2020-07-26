function toggle_h(h) {
    var d = h.next("div");
    var i = h.find("i[class^='fas fa-caret']");

    // close all other sections
    const lookup = h.is("h1") ? ["div.module", "h1.module-doc"] : ["div.module-doc", "h2.command-doc"]
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

$(document).ready(function(){
    const h = $($(location).attr('hash'));
    if(h.length) {
        toggle_h(h);
    }
});

// nav link
$(document).on('click', 'table.bot-categories td', function(e){
    e.preventDefault();
    var l = $(this).children("a").attr("href").split("/")[2];
    $( "#content-update" ).load( "/bot/"+l+"/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }, nav("/bot/"+l+"/"));
    $("#content-update h2").html(spinner+'&nbsp;&nbsp;Loading')
    $("#content-update h2").addClass("grey");
    $("div.error").hide();
});

// update discord id
$(document).on('click', '#discord-update-id', function(e){
    e.preventDefault();
    var reload = $("#discord-id");
    reload.load( "/bot/updateId/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.html('<p>'+spinner+'</p>');
});

// toggle perm
$(document).on('click', '#discord-toggle-perm', function(e){
    e.preventDefault();
    // var r = confirm("I accept to give the official YATA bot access to my API key");
    var r = true;
    if (r == true) {
      var reload = $("#discord-perm");
      reload.load( "/bot/togglePerm/", {
          csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
      });
      reload.html('<p>'+spinner+'</p>');
    }
});

// toggle notifications
$(document).on('click', "td[id^='discord-toggle-pref-']", function(e){
    e.preventDefault();
    var reload = $(this);
    var type = reload.attr("id").split("-").pop()
    reload.load( "/bot/toggleNoti/", {
        type: type,
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }).html(''+spinner+'');
});

// show/hide command
$(document).on('click', 'h1.module-doc, h2.command-doc', function(e){
    e.preventDefault();
    // get h2 and div
    var h = $(this);
    toggle_h(h);
});
