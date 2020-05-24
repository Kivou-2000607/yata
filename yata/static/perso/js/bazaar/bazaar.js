// nav link
$(document).on('click', 'table.bazaar-categories td', function(e){
    e.preventDefault();
    var l = $(this).children("a").attr("href").split("/")[2];
    $( "#content-update" ).load( "/bazaar/"+l+"/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }, nav("/bazaar/"+l+"/"));
    $("#content-update h2").html(spinner+'&nbsp;&nbsp;Loading '+l)
    $("#content-update h2").addClass("grey");
    $("div.error").hide();
});



// show/hide details item
$(document).on('click', '.details-item', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#details-item" ).load( "/bazaar/details/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
});
$(document).on('click', '.prices-item', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#prices-item" ).load( "/bazaar/prices/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
});
$(document).on('click', 'tr.abroad-item-stocks > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var item_id = $(this).parent("tr").attr("data-ite");
    var country_key = $(this).parent("tr").attr("data-cou");
    $( "#prices-item" ).load( "/bazaar/abroad/stocks/", {
        item_id: item_id, country_key: country_key, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
});
$(document).on('click', '.close', function(e){
    e.preventDefault();
    $(this).parent("div.container").css("display", "none");
});

// update item
$(document).on('click', '.update-item', function(e){
    e.preventDefault();
    if ($(this).hasClass("lock")) {
        console.log("cooldown");
    } else {
        var tId = $(this).attr("href").split("/").pop();
        $( "#item-sell-table-" + tId ).load( "/bazaar/update/"+tId, {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        });
        $(this).children("button").html('<i class="fas fa-spinner fa-pulse"></i>');
    }
});

// update type
$(document).on('click', '.update-type', function(e){
    e.preventDefault();
    var tType = $(this).attr("href").split("/").pop();
    var i = 1;
    $("#loop-over-item-sell-table-"+tType).find('table[id^="item-sell-table-"]').each(function() {
        var reload = $(this);
        var tId = $(this).attr("id").split("-").pop();
        var wait = i*500 + parseInt(i/10)*3000;
        (function(index) {
            setTimeout(function() {
                reload.load( "/bazaar/update/"+tId, {
                    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                });
                reload.find("button").html('<i class="fas fa-spinner fa-pulse"></i>');
             }, wait);
        })(i);
        i++;
    });
});

// delete item
$(document).on('click', '.delete-item', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#item-sell-table-" + tId ).load( "/bazaar/delete/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    $(this).closest("thead").children("tr:first-child").children("th").children("div").children("form").children("a").children("button").html('<i class="fas fa-spinner fa-pulse"></i>');
});

// toggle item
$(document).on('click', '.toggle-item', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#item-sell-table-" + tId ).load( "/bazaar/toggle/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    $(this).closest("thead").children("tr:first-child").children("th").children("div").children("form").children("a").children("button").html('<i class="fas fa-spinner fa-pulse"></i>');
});

// refresh timer update
window.setInterval(function(){
    $("a.update-timer").each(function() {
        table = $(this).closest("table");
        var updatetime = $.trim($(this).text());
        if ( updatetime.search(" s")!=-1 ) {
            var splt = updatetime.split(" ");
            var seconds = 0;
            if (splt.length == 2) {
                seconds = parseInt(splt[0]);
            } else if (splt.length == 4) {
                seconds = parseInt(splt[2]) + 60 * parseInt(splt[0]);
            }

            // if ( seconds > 10 ) {
            //     console.log(table.find(".lock"));
            // }

            if ( seconds > 599 ) {
                $(this).html("> 10 mins");
                // table.addClass("old-refresh");
            } else {
                seconds ++;
                minutes = Math.floor(seconds / 60);
                seconds = seconds % 60;
                if (minutes) {
                    spad = ("0"+seconds.toString()).slice(-2);
                    $(this).html(minutes.toString()+" mins "+spad+" s");
                } else {
                    $(this).html(seconds.toString()+" s");
                }
                // table.removeClass("old-refresh");
            }
        }
        // else {
        //     if (!table.hasClass('old-refresh')) {
        //         table.addClass('old-refresh');
        //     }
        // }
    });
}, 1000);


// show/hide module
$(document).on('click', 'h3.toggle-display', function(e){
    e.preventDefault();
    var h = $(this);
    var c = h.next("pre");
    var i = h.find("i");
    if (c.is(":hidden")) i.addClass("fa-rotate-90"); else i.removeClass("fa-rotate-90");
    c.slideToggle("fast");
});



// toggle abroad filters
$(document).on('click', "td.bazaar-toggle-filters", function(e){
    e.preventDefault();
    var td = $(this);
    var filter = td.attr("data-fil");
    var key = td.attr("data-key");
    var reload = $(e.currentTarget).parents("div#bazaar-abroad-stocks-reload");
    // var divspinner = '<div style="text-align: center; height: '+reload.css("height")+';">'+spinner+'</div>'
    reload.load( "/bazaar/abroad/", {
        key: key, filter: filter, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
    td.html(spinner);
    $("table#bazaar-abroad-stocks").find("tbody").find("td").html(spinner);
});
