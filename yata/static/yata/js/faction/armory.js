// drop down armory record
$(document).on('click', '.faction-armory-toggle-view', e=>{
    e.preventDefault();
    $(e.currentTarget).next("table").slideToggle("fast", ()=>{
        $(e.currentTarget).find("i.fa-caret-right").toggleClass("fa-rotate-90");
    });
});


// show/hide breakdown
$(document).on('click', 'h1.faction-armory-type', function(e){
    e.preventDefault();
    var h = $(this);
    var d = $(this).next("div");
    var i = h.find("i[class^='fas fa-caret']");
    d.slideToggle("fast", function(){
        if (d.css("display") == "none") {
            i.removeClass("fa-rotate-90");
        } else {
            i.addClass("fa-rotate-90");
        }
    });
});

// filter by member
$(document).on('click', 'form.news > i.filter-player,form.news > i.filter-player-activated', e=>{
    e.preventDefault();
    console.log("news")
    var member = $(e.currentTarget).attr("data-val");
    var start = $(e.currentTarget).attr("data-start");
    var end = $(e.currentTarget).attr("data-end");
    var reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( "/faction/armory/news/", {
        member: member, type: "filter", start: start, end: end,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html('<td>'+spinner+'</td>');
});

$(document).on('change', 'select.faction-armory-header-filter', e=>{
    e.preventDefault();
    $("#content-update").load( "/faction/armory/", {
        member: $(e.currentTarget).val(), type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Filtering armory');
});

$(document).on('click', '#faction-armory-reset-filters', e=>{
    e.preventDefault();
    $("#content-update").load( "/faction/armory/", {
        resetFilters: 1,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Reset armory filters');
});
