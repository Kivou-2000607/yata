// update history on load
const afterLoad = (r,s,x) =>{
    window.history.pushState(null, document.title, x.url);
};

// parse cookie
const getCookie = (s)=>{
    let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
    return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
};

//Store repeated html string (spinner)
const spinner = '<i class="fas fa-spinner fa-pulse"></i>';

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
