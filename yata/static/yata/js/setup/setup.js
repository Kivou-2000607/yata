// show/hide breakdowns
$(document).on("click", "tr.h-a", (e) => {
    e.preventDefault();
    $(e.target).find("i.fa-caret-right").toggleClass("fa-rotate-90");
    $(e.target).parents("table").find(".h-b").toggle();
});