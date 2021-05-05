// show/hide details item
$(document).on('click', 'tr.abroad-item-stocks > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var item_id = $(this).parent("tr").attr("data-ite");
    var country_key = $(this).parent("tr").attr("data-cou");
    $( "#bazaar-modal" ).load( "/bazaar/abroad/stocks/", {
        item_id: item_id, country_key: country_key, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
});


// header click
$(document).on('click', '.item-table-header:not(.no-click)', e=>{
    e.preventDefault();

    // get item data and DOM
    const action = $(e.currentTarget).attr('data-act');
    const item_table = $(e.currentTarget).parents('.item-table');
    const item_id = $(item_table).attr('data-iid');

    if( action == "update" ) {
      $(item_table).load( "/bazaar/update/"+item_id, { csrfmiddlewaretoken: getCookie("csrftoken"), });
      $(e.currentTarget).find("button").html('<i class="fas fa-spinner fa-pulse"></i>');
    } else if (action == "delete") {
      $(item_table).load( "/bazaar/delete/"+item_id, { csrfmiddlewaretoken: getCookie("csrftoken"), });
      $(e.currentTarget).html('<i class="fas fa-spinner fa-pulse"></i>');
    } else if (action == "details") {
      $( "#bazaar-modal" ).load( "/bazaar/details/"+item_id, { csrfmiddlewaretoken: getCookie("csrftoken"), });
    } else if (action == "toggle") {
      $(item_table).load( "/bazaar/toggle/"+item_id, { csrfmiddlewaretoken: getCookie("csrftoken"), });
    } else if (action == "prices") {
      $( "#bazaar-modal" ).load( "/bazaar/prices/"+item_id, { csrfmiddlewaretoken: getCookie("csrftoken"), });
    }
});

// show more/less
$(document).on('click', 'tr.show-more', e=>{
    e.preventDefault();
    $(e.currentTarget).removeClass("d-table-row").hide();
    $(e.currentTarget).siblings().removeClass("d-none");
    $(e.currentTarget).siblings(".show-less").addClass("d-table-row").show();
});
// show more/less
$(document).on('click', 'tr.show-less', e=>{
    e.preventDefault();
    $(e.currentTarget).removeClass("d-table-row").hide();
    $(e.currentTarget).siblings().not(".keep-showing").not(".show-more").addClass("d-none");
    $(e.currentTarget).siblings(".show-more").addClass("d-table-row").show();
});

// update type
$(document).on('click', 'span.update-type', e=>{
    e.preventDefault();
    const type = $(e.currentTarget).attr("data-val");
    let i = 1;
    $("#loop-over-item-sell-table-"+type).find('div.item-table').each(function() {
        let item_table = $(this)
        let item_id = $(this).attr("data-iid");
        let wait = i*500 + parseInt(i/10)*3000;
        (function(index) {
            setTimeout(function() {
                $(item_table).load( "/bazaar/update/"+item_id, { csrfmiddlewaretoken:  getCookie("csrftoken"), });
                $(item_table).find("button").html('<i class="fas fa-spinner fa-pulse"></i>');
             }, wait);
        })(i);
        i++;
    });
});

// refresh timer update
window.setInterval(function(){
    $(".update-timer").each(function() {
        var tsUpdate = parseInt($(this).attr("data-val"));
        var tsNow = parseInt(Date.now() / 1000)

        if ( tsNow - tsUpdate > 300 ) {
            $(this).html("> 5 min");
            $(this).removeClass("update-timer")
        } else {
            $(this).html(fancyTimeFormat(tsNow - tsUpdate))
        }
    });
}, 1000);


// toggle abroad filters
$(document).on('click', "li.bazaar-toggle-filters", function(e){
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
    $("table#bazaar-abroad-stocks").find("tr").html('<td colspan="9" style="text-align: center;">'+spinner+'</td>');
    // $("table#bazaar-abroad-stocks").find("tbody").find("td").html('<i class="fas fa-spinner"></i>');
});
