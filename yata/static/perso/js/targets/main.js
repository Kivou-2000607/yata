$(document).on('click', 'table.target-categories td', function(e){
    e.preventDefault();
    var l = $(this).children("a").attr("href").split("/")[2];
    $( "#content-update" ).load( "/target/"+l+"/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }, nav("/target/"+l));
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(spinner+'&nbsp;&nbsp;Loading '+l)
    $("div.error").hide();
});
