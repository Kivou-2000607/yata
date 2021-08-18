$(document).on("click", "table#target-dogtags > tbody > tr > td:not(.dont-touch-me)", (e) => {
    e.preventDefault();
    const tr = $(e.target).parents("tr");
    const uid = tr.attr("data-uid");
    const los = tr.attr("data-los");
    $("#target-dogtags-compare").load("/target/dogtags/", {
        uid, los, type: "compare",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(`<div class="container"><div class="overlay close"></div><div class="modal-center-large"><div class="module" ><p>${spinner}</p></div></div></div>`);
});

// delete target from target list button
$(document).on("click", "a.target-dogtags-delete", (e) => {
    e.preventDefault();
    const tr = $(e.target).parents("tr");
    const uid = tr.attr("data-uid");
    tr.load("/target/dogtags/", {
        uid, type: "delete",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    tr.remove();
});

// delete target from overlay
$(document).on("click", "a.target-dogtags-delete-overlay", (e) => {
    e.preventDefault();
    const uid = $(e.target).attr("data-uid");
    const tr = $(`tr[data-uid="${uid}"]`);
    tr.load("/target/dogtags/", {
        uid, type: "delete",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("div.container").remove();
    tr.remove();
});

// add failed attack target from target list button
$(document).on("click", "a.target-dogtags-add", (e) => {
    e.preventDefault();
    const tr = $(e.target).parents("tr");
    const uid = tr.attr("data-uid");
    tr.load("/target/dogtags/", {
        uid, type: "add",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(`<td colspan="9">${spinner}</td>`);
});

// add failed target from overlay
$(document).on("click", "a.target-dogtags-add-overlay", (e) => {
    e.preventDefault();
    const uid = $(e.target).attr("data-uid");
    const tr = $(`tr[data-uid='${uid}']`);
    tr.load("/target/dogtags/", {
        uid, type: "add",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(`<td colspan="9">${spinner}</td>`);
    $("div.container").remove();
});

// check target
$(document).on("click", "a.target-dogtags-clean", (e) => {
    e.preventDefault();
    let i = 1;
    $("tr.target-dogtag").each((useless, e) => {
        const tr = $(e);
        const uid = tr.attr("data-uid");
        const wait = i * 1000 + parseInt(i / 10) * 4000;
        ((index) => {
            setTimeout(() => {
                console.log(uid, i, wait);
                tr.load("/target/dogtags/", {
                    uid, type: "clean",
                    csrfmiddlewaretoken: getCookie("csrftoken"),
				}).html(`<td colspan="9">${spinner}</td>`);
            }, wait);
        })(i);
        i++;
    });
});
