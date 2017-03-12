loadCSS('src/style.css');

if (typeof(data) != "undefined") {
    console.log(data);
    result = {};
    $.each(data, function(k, v) {
        result[k] = v['data'];
    });
    var app = angular.module("data", []);
    app.controller("list", function ($scope, $http) {
        $scope.result = result;
        //$scope.items = data["e70e381a-29a9-4361-ba47-bce3b2e72348"]["data"];
    });
} else if (typeof(draw) != "undefined") {
    var app = angular.module("draw", []);
    app.filter('reverse', function() {
        return function(items) {
            return items.slice().reverse();
      };
    });
    app.controller("list", function ($scope, $http) {
        $scope.result = draw;
        //$scope.items = data["e70e381a-29a9-4361-ba47-bce3b2e72348"]["data"];
    });
}

$(function() {
    loadScript('src/bootstrap.min.js');
    var $doc = $(document);
    var $wind = $(window);
    var hb_js = function() {
        hb_scroll_top_init();
        hb_to_top_click();
    };
    var pathname = urlParser(window.location.href).pathname;
    var nav = document.createElement('nav');
    nav.setAttribute('class', 'navbar navbar-default navbar-fixed-top');
    $('body').prepend(nav);
    var navObj = $('body nav:first-child');
    navObj.next().css({'margin-top': navObj.height()});
    $('body > nav').append('<div class="container-fluid">');
    $('body > nav > div.container-fluid').append('<div class="navbar-header"> <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse-1" aria-expanded="true"> <span class="sr-only">Toggle navigation</span> <span class="icon-bar"></span> <span class="icon-bar"></span> <span class="icon-bar"></span> </button> <a href="javascript:void(0);" onclick="window.location.reload();" class="navbar-brand">刷新</a> </div>').append('<div class="collapse navbar-collapse" id="bs-navbar-collapse-1"><ul class="nav navbar-nav"><li><a href="'+ (pathname.indexOf('/output.html') >= 0 ? 'record.html">抽奖记录' : 'output.html">测水记录') + '</a></li></ul></div>');

})

function loadCSS(url){
    var cssLink = document.createElement("link");
    cssLink.rel = "stylesheet";
    cssLink.rev = "stylesheet";
    cssLink.type = "text/css";
    cssLink.media = "screen";
    cssLink.href = url;
    document.getElementsByTagName("head")[0].appendChild(cssLink);
}

function loadScript(url, callback) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    if(typeof(callback) != "undefined"){
        if (script.readyState) {
            script.onreadystatechange = function () {
                if (script.readyState == "loaded" || script.readyState == "complete") {
                    script.onreadystatechange = null;
                    callback();
                }
            };
        } else {
            script.onload = function () {
                callback();
            };
        }
    }
    script.src = url;
    document.body.appendChild(script);
}

function urlParser(url) {
    var el = document.createElement('a');
    el.href = url;
    return el;
}
