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
