window.URL = window.location.pathname;
var months = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

function decideType(url) {
  if (url.split("/")[1] != "correlations") {
    window.cor = 0;
  } else if (url.split("/")[3] == "ann" || url.split("/")[3] == "mon") {
    window.cor = 1;
  } else {
    window.cor = 2;
  }
}

decideType(window.URL);

function setSpacerHeight(h) {
  document.getElementById("spacer").style.height = h.toString().concat("px");
}

function setMenuPosition(name, o) {
  document.getElementById(name).style.left = o.toString().concat("px");
}

function pageReadyNav() {
  var h = document.getElementById("navbar").offsetHeight;
  setSpacerHeight(h);
}

function pageReadyActives(A) {
  if (window.cor != 2) {
    if (window.cor == 0) {
      if (A != undefined) {
        window.stat = A[1];
        if (A[2] == "mon") {
          window.mon = A[3];
        } else {
          window.mon = "A";
        }
      } else {
        window.stat = "tasmax";
        window.mon = "A";
      }
      document.getElementById("normal").classList += " active";
    } else if (window.cor == 1) {
      window.stat = A[2];
      if (A[3] == "mon") {
        window.mon = A[4];
      } else {
        window.mon = "A";
      }
      document.getElementById("correlations1").classList += " active";
    }
    document.getElementById(window.stat).classList += " active";
    if (window.mon != "A") {
      document.getElementById(months[window.mon]).classList += " active";
      document.getElementById("mon").classList += " active";
    } else {
      document.getElementById("ann").classList += " active";
    }
  } else if (window.cor == 2) {
    window.stat1 = A[2];
    window.stat2 = A[3];
    if (A[4] == "mon") {
      window.mon = A[5];
    } else {
      window.mon = "A";
    }
    document.getElementById(window.stat1.concat("1")).classList += " active";
    document.getElementById(window.stat2.concat("2")).classList += " active";
    document.getElementById("correlations2").classList += " active";
    if (window.mon != "A") {
      document.getElementById(months[window.mon]).classList += " active";
      document.getElementById("mon").classList += " active";
    } else {
      document.getElementById("ann").classList += " active";
    }
  }
}

function pageReadyTitle() {
  var monthSpan = document.getElementById("month");
  if (monthSpan != null) {
    monthSpan.innerHTML = months[window.mon];
  }
}

function toggleResponsive() {
  var x = document.getElementById("navbar");
  if (x.className === "") {
    x.className += " responsive";
    setSpacerHeight(0);
  } else {
    x.className = "";
    setSpacerHeight(h);
  }
}

// Mother function for changePage, back is either 'y' or 'n' depending on
// if you called from the backbutton ('popstate') or not.

function changePageMother(url, back) {
  window.URL = url;
  decideType(window.URL);

  if (url === "/" || window.location.pathname == "/") {
    window.location.href = url;
  } else {
    $.get(url, function (data) {
      window.e1 = $(data).find("#graph");
      window.e2 = $(data).find("#after");
      window.e3 = $(data).find("#navWrapperInner");
      $("#graph").replaceWith(window.e1);
      $("#after").replaceWith(window.e2);
      $("#navWrapperInner").replaceWith(window.e3);
    }).done(function () {
      MathJax.typeset();
      pageReadyNav();
      pageReadyActives(window.URL.split("/"));
      if (window.cor == 0 || window.cor == 2) {
        updatelatLon(window.latLon);
      } else if (window.coords != undefined) {
        updatelatLon2(window.coords[0], window.coords[1]);
      }
    });
    if (back == "n") {
      window.history.pushState("object or string", "Title", url);
    }
  }
}

function changePage(url) {
  return changePageMother(url, "n");
}

$(window).bind("popstate", function () {
  pn = window.location.pathname;
  if (pn != "/"){
    changePageMother(pn, "y");
  }
  pageReadyNav();
  pageReadyActives();
  pageReadyTitle();
});

function updatelatLon(l) {
  if (l != undefined) {
    var data = { lat: l["lat"], lon: l["lng"] };
    $.post(window.URL, data, function (data) {
      console.log($("my_plot", data));
      $("#my_plot").replaceWith($("#my_plot", data));
      $("#cCoeff").replaceWith($("#cCoeff", data));
      document.getElementById("start").style.display = "none";
      document.getElementById("after").style.display = "block";
    }).fail(function () {
      alert(
        "No data availible for the selected point. Probably you choose somewhere in the ocean or a place in Ireland! Please try again"
      );
    });
  }
}

function updatelatLon2(l1, l2) {
  if (l1 != undefined && l2 != undefined) {
    var data = {
      lat1: l1["lat"],
      lon1: l1["lng"],
      lat2: l2["lat"],
      lon2: l2["lng"],
    };
    $.post(window.URL, data, function (data) {
      $("#my_plot").replaceWith($("#my_plot", data));
      $("#cCoeff").replaceWith($("#cCoeff", data));
      document.getElementById("start").style.display = "none";
      document.getElementById("after").style.display = "block";
    }).fail(function () {
      alert(
        "No data availible for at least one of the points you selected. Probably you choose somewhere in the ocean or a place in Ireland! Please try again"
      );
    });
  }
}

function checkIfMB(f) {
  if (!mapboxgl.supported) {
    alert(
      "Your browser does not support Mapbox GL, you won't be able to use this site. Please upgrade your browser and try again"
    );
  } else {
    f();
  }
}

function mkPage1() {
  pageReadyNav();
  pageReadyActives(window.URL.split("/"));

  mapboxgl.accessToken = window.mb_token;

  if ($("#map").html() == "") {
    document.getElementById("start").style.display = "block";
    var map = new mapboxgl.Map({
      container: "map", // container id
      style: "mapbox://styles/mapbox/streets-v11", // stylesheet location
      center: [-3.6, 54.83], // starting position [lng, lat]
      zoom: 4.5, // starting zoom
      interactive: false,
    });

    $(window).resize(function () {
      map.fitBounds([
        [-7.2, 49.5],
        [1.2, 60],
      ]);
    });

    var el = document.createElement("span");
    el.className = "marker";
    var marker = new mapboxgl.Marker(el);
    var currentMarkers = [];

    map.on("click", function (e) {
      window.latLon = e.lngLat;
      updatelatLon(window.latLon);
      if (currentMarkers !== null) {
        for (var i = currentMarkers.length - 1; i >= 0; i--) {
          currentMarkers[i].remove();
        }
      }
      marker.setLngLat(window.latLon);
      el.innerHTML =
        '<span class="markertext"> ( lng, lat ) = ( ' +
        e.lngLat["lng"].toFixed(2) +
        ", " +
        e.lngLat["lat"].toFixed(2) +
        " )</span>";
      marker.addTo(map);
      currentMarkers.push(marker);
    });
  }
}

function mkPage2() {
  window.currentMarkers = [];

  pageReadyActives(window.URL.split("/"));
  pageReadyNav();

  mapboxgl.accessToken = window.mb_token;

  if ($("#map").html() == "") {
    document.getElementById("start").style.display = "block";
    window.map = new mapboxgl.Map({
      container: "map", // container id
      style: "mapbox://styles/mapbox/streets-v11", // stylesheet location
      center: [-3.6, 54.83], // starting position [lng, lat]
      zoom: 4.5, // starting zoom
      interactive: false,
    });

    $(window).resize(function () {
      window.map.fitBounds([
        [-7.2, 49.5],
        [1.2, 60],
      ]);
    });

    window.el1 = document.createElement("span");
    window.el1.classname = "marker";

    window.el2 = document.createElement("span");
    window.el2.classname = "marker";

    window.map.on("click", function (e) {
      if (window.currentMarkers.length == 0) {
        if (window.marker1 != undefined) {
          window.marker1.remove();
        }
        if (window.marker2 != undefined) {
          window.marker2.remove();
        }
        window.currentMarkers = [];
        window.coords = [];
        window.marker1 = new mapboxgl.Marker(window.el1);
        window.latLon = e.lngLat;
        window.coords.push(e.lngLat);
        window.marker1.setLngLat(window.latLon);
        window.el1.innerHTML =
          '<span class="marker">' +
          '<span class="markertext">' +
          " Please choose another point! " +
          "</span></span>";
        window.marker1.addTo(map);
        window.currentMarkers.push(window.marker1);
      } else if (window.currentMarkers.length == 1) {
        window.marker2 = new mapboxgl.Marker(el2);
        window.latLon = e.lngLat;
        window.coords.push(e.lngLat);
        updatelatLon2(window.coords[0], window.coords[1]);
        window.currentMarkers.push(window.marker2);
        window.marker2.setLngLat(window.latLon);
        window.el2.innerHTML =
          '<span class="marker">' +
          '<span class="markertext"> ( lng, lat ) = ( ' +
          e.lngLat["lng"].toFixed(2) +
          ", " +
          e.lngLat["lat"].toFixed(2) +
          " )</span></span>";
        window.el1.innerHTML =
          '<span class="marker">' +
          '<span class="markertext"> ( lng, lat ) = ( ' +
          window.coords[0]["lng"].toFixed(2) +
          ", " +
          window.coords[0]["lat"].toFixed(2) +
          " )</span></span>";
        window.marker2.addTo(map);
      } else {
        window.marker1.remove();
        window.marker2.remove();
        window.currentMarkers = [];
        window.coords = [];
        window.marker1 = new mapboxgl.Marker(el1);
        window.latLon = e.lngLat;
        window.coords.push(e.lngLat);
        window.marker1.setLngLat(window.latLon);
        window.el1.innerHTML =
          '<span class="marker">' +
          '<span class="markertext">' +
          " Please choose another point! " +
          "</span></span>";
        window.marker1.addTo(map);
        window.currentMarkers.push(window.marker1);
      }
    });
  }
}

$(document).ready(function () {
  if (window.URL != "/") {
    if (window.cor == 0 || window.cor == 2) {
      checkIfMB(mkPage1);
    } else {
      checkIfMB(mkPage2);
    }
  }
});

var mutationObserver = new MutationObserver(function (mutations) {
  mutations.forEach(function (mutation) {
    pageReadyNav();
  });
});

mutationObserver.observe(document.documentElement, {
  attributes: true,
  characterData: true,
  childList: true,
  subtree: true,
  attributeOldValue: true,
  characterDataOldValue: true,
});
