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
