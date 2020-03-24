// categories
$(document).on('click', 'table.stock-categories td', function(e){
    e.preventDefault();
    var l = $(this).children("a").attr("href").split("/")[2];
    var t = $(this).children("a").attr("href").split("/")[3];
    console.log(l);
    console.log($(this).children("a").attr("href").split("/"));
    $( "#content-update" ).load( "/stock/"+l+"/"+t, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html('<i class="fas fa-spinner fa-pulse"></i>&nbsp;&nbsp;Loading '+l)
    $("div.error").hide();
});

// open details and prices
$(document).on('click', '.stock-details', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#stock-details" ).load( "/stock/details/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
});
$(document).on('click', '.stock-prices', function(e){
    e.preventDefault();
    var tId = $(this).attr("href").split("/").pop();
    $( "#stock-prices" ).load( "/stock/prices/"+tId, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
});
$(document).on('click', '.graph-period-selector', function(e){
    e.preventDefault();
    var tId = $(this).children("input").val().split("-")[0];
    var period = $(this).children("input").val().split("-")[1];
    console.log(tId, period);
    $( "#stock-prices-graphs" ).load( "/stock/prices/"+tId+"/"+period, {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    $(this).addClass('fas fa-spinner fa-pulse');
});
$(document).on('click', '.close', function(e){
    e.preventDefault();
    $(this).parent("div.container").css("display", "none");
});
