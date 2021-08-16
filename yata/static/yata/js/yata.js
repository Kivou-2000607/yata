$(document).on("click", "#yata-login-submit", (e) => {
	e.preventDefault();

	// WARNING: IT IS NOT TOLERATED TO MODIFY THIS FUNCTION
	// as it will remove the warning when users enter their API key on non official instances of YATA.
	// Changing it will be seen as making your instance of YATA looks official, thus raising suspicions.
	if (window.location.host !== "yata.yt") {
		if (
			confirm(
				"This is not the official YATA website which is hosted on https://yata.yt.\nWhere it is allowed to host instances of YATA on personal servers, make sure you know who's hosting it and that they have no malicious intents.\n\nKivou [2000607]"
			) === false
		) {
			return;
		}
	}

	$("#header").load("/login", {
		key: $("#yata-login-key").val(),
		csrfmiddlewaretoken: getCookie("csrftoken"),
	});
	$(e.target).html(spinner);
});

$(document).on("click", "#yata-logout-submit", (e) => {
	$(e.target).html(spinner);
});

$(document).on("click", "#yata-delete-submit", (e) => {
	if (confirm("Are you sure you want to delete your account? All data will be removed from the database.") === false) {
		e.preventDefault();
	}
});

$(document).on("click", "#yata-toggle-color-mode", (e) => {
	e.preventDefault();

	$(e.target)
		.parent("div")
		.parent("div")
		.load("/update_session", {
			key: "dark",
			csrfmiddlewaretoken: getCookie("csrftoken"),
		});

	// dynamically load dark/light mode upon toggle
	// (get the filename from data attr because of whitenoise random slug)
	const cssFile = e.target.dataset.cssFile;
	const oldLightCSS = document.querySelectorAll("head link[href*='/static/yata/css/css-vars-light']");
	const oldDarkCSS = document.querySelectorAll("head link[href*='/static/yata/css/css-vars-dark']");
	const fileref = $("<link>", {
		rel: "stylesheet",
		type: "text/css",
		href: cssFile,
	})[0];
	document.head.appendChild(fileref);
	oldLightCSS.forEach((x) => x.remove());
	oldDarkCSS.forEach((x) => x.remove());

	document.body.classList.toggle("dark");
});

const spinner = "<i class='fas fa-spinner fa-pulse'></i>";

function toggle_h(h) {
	const d = h.next("div");
	const i = h.find("i[class^='fas fa-caret']");

	// close all other sections
	const lookup = h.is("h3") ? ["div.module", "h3.module-doc"] : ["div.module-doc", "h4.command-doc"];
	h.closest(lookup[0])
		.find(lookup[1])
		.each((i, item) => {
			if (item != h[0]) {
				$(item).next("div").slideUp("fast");
				$(item).find("i[class^='fas fa-caret']").removeClass("fa-rotate-90");
			}
		});

	// toggle
	d.slideToggle("fast", () => {
		if (d.css("display") == "none") {
			i.removeClass("fa-rotate-90");
		} else {
			i.addClass("fa-rotate-90");
		}
	});
}

// show/hide command
$(document).on("click", "h3.module-doc, h4.command-doc", (e) => {
	e.preventDefault();
	// get h2 and div
	toggle_h($(e.target));
});

function fancyCountdown(time) {
	// From https://stackoverflow.com/a/11486026
	// days:hours:minutes:seconds
	const days = ~~(time / 86400);
	const hrs = ~~((time % 86400) / 3600);
	const mins = ~~((time % 3600) / 60);
	const secs = ~~time % 60;

	let ret = "";

	if (days > 0) {
		ret += "" + days + " day" + (days !== 1 ? "s " : " ");
	}

	ret += hrs < 10 ? "0" : "";
	ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
	ret += "" + mins + ":" + (secs < 10 ? "0" : "");
	ret += "" + secs;
	return ret;
}

function fancyTimeFormat(time) {
	// From https://stackoverflow.com/a/11486026
	// Hours:minutes:seconds
	const hrs = ~~(time / 3600);
	const mins = ~~((time % 3600) / 60);
	const secs = ~~time % 60;

	let ret = "";

	if (hrs > 0) {
		ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
	}

	ret += "" + mins + ":" + (secs < 10 ? "0" : "");
	ret += "" + secs;
	return ret;
}

function nav(url) {
	console.log("nav" + url);
	window.history.pushState(null, document.title, url);
}

// const nav = (r,s,x,url) =>{
//     console.log(r);
//     console.log(s);
//     console.log(x);
//     console.log(url);
//     window.history.pushState(r, document.title, url);
// };

// parse cookie
function getCookie(s) {
	const parse = RegExp("" + s + "[^;]+").exec(document.cookie);
	return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./, "") : "");
}

// header navigation
$(document).on("click", "div.yt-main-link a", (e) => {
	const h2 = $("#content-update h2");
	h2.addClass("grey");
	h2.html(`${spinner}&nbsp;Loading ${e.currentTarget.getAttribute("title")}`);
	$(e.currentTarget).find("i").replaceWith(spinner);
});

// sub header navigation
$(document).on("click", "div.yt-cat-link", (e) => {
	e.preventDefault();
	const link = $(e.currentTarget).children("a");
	$("#content-update").load(
		link.getAttribute("href"),
		{
			csrfmiddlewaretoken: getCookie("csrftoken"),
		},
		nav(link.getAttribute("href"))
	);
	$("#content-update h2")
		.addClass("grey")
		.addClass("px-2")
		.html(`<div class="ps-2">${spinner}&nbsp;Loading ${link.getAttribute("title")}</div>`);
	$("div.error").hide();
});

// pagination nav
$(document).on("click", "a.yt-page-link", (e) => {
	e.preventDefault();
	const reload = e.currentTarget.closest("div.pagination-list");
	reload.load(e.currentTarget.getAttribute("href"), () => {});
	$(e.currentTarget).closest("table").find("tr").html(`<td colspan="*" class="text-center">${spinner}</td>`);
});

// prevent show/hide
$(document).on("click", "h2.title.toggle-display div.no-click", (e) => {
	const h = e.target.closest("h2");
	const div = h.next("div");
	const i = h.find("div.toggle-rotate").find("i");
	if (div.css("display") == "none") {
		h.removeClass("rounded").removeClass("mb-3");
		i.classList.add("fa-rotate-90");
	} else {
		e.stopPropagation();
	}
});

// show/hide module
$(document).on("click", "h2.title.toggle-display", (e) => {
	e.preventDefault();
	const h = e.target.closest("h2");
	if (!($(e.target).hasClass("update-type") && !h.hasClass("rounded"))) {
		const i = h.find("div.toggle-rotate").find("i");
		const div = h.next("div");
		if (div.css("display") === "none") {
			h.removeClass("rounded").removeClass("mb-3");
			i.addClass("fa-rotate-90");
		}
		div.slideToggle("fast", () => {
			if (div.css("display") === "none") {
				h.addClass("rounded").addClass("mb-3");
				i.removeClass("fa-rotate-90");
			}
		});
	}
});

// refresh loot timer
let lootTimer = document.querySelector("span#loot-countdown-header");
window.setInterval(() => {
	if (!lootTimer) lootTimer = document.querySelector("span#loot-countdown-header");
	const loot = parseInt($.trim(lootTimer.dataset.lts));
	const name = $.trim(lootTimer.dataset.nam);
	const tid = $.trim(lootTimer.dataset.tid);
	const now = Date.now() / 1000;
	const diff = loot - now;

	let cd = fancyTimeFormat(diff);
	let cl = "";

	if (diff < 60) {
		cd = "now";
	}

	if (diff < 60 * 5) {
		cl = "error";
	} else if (diff < 60 * 15) {
		cl = "warning";
	}

	$(lootTimer).html(`<a class="${cl}" href="https://www.torn.com/loader.php?sid=attack&user2ID=${tid}" target="_blank">${name}: ${cd}</a>`);
}, 1000);

//
// $(document).on("click", ".overlay.close", function(e){
//     e.preventDefault();
//     $(this).parent("div.container").css("display", "none");
// });
//
// $(document).on("click", ".close-button", function(e){
//     e.preventDefault();
//     $(this).closest("div.container").css("display", "none");
// });
//

// full width
$(document).on("click", ".yt-full-width", (e) => {
	e.preventDefault();
	$("#main-content").css("max-width", "100%");
	$(e.target).closest("li").hide();
});
