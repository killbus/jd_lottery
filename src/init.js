loadCSS('src/style.css');

var pathname = urlParser(window.location.href).pathname;
var target = pathname.indexOf('/output.html') >= 0 ? 'output' : pathname.indexOf('/record.html') >= 0 ? 'record' : '';
var timer;

if (target == 'output') {
    var app = angular.module("data", []);
    app.controller("list", function ($scope, $http, $location, $anchorScroll, $timeout) {
        loadScript('src/data.js?ver='+Math.random().toString(16), dataInit, {'elem': document.getElementById('init'), 'po': 'before'});    
        $scope.gotoScroll = function(id) {
            // set the location.hash to the id of
            // the element you wish to scroll to.
            $location.hash(id);

            // call $anchorScroll()
            $anchorScroll();
        };
        function dataInit() {
            $timeout(function() {
                if (typeof(data) != "undefined") {
                    console.log(data);
                    result = {};
                    $.each(data, function(k, v) {
                        result[k] = v['data'];
                    });
                    $scope.result = result;
                    $timeout(hashLocator, 0);
                }
            }, 0);
        }
        function hashLocator() {
                var hash = window.location.hash;
                var id = window.location.hash.replace(/^#\//g, '');
                if (id && $('#'+id).length > 0) {
                    $anchorScroll.yOffset = $('body').offset().top;
                    $scope.gotoScroll(id);
                }
                $('#refresh').text('（10秒后刷新）');
                refresh();
        }
        //$scope.items = data["e70e381a-29a9-4361-ba47-bce3b2e72348"]["data"];
    });
} else if (target == 'record') {
    var app = angular.module("draw", []);
    app.filter('reverse', function() {
        return function(items) {
            return items.slice().reverse();
      };
    });
    app.controller("list", function ($scope, $http, $timeout) {
        loadScript('src/draw.js?ver='+Math.random().toString(16), dataInit, {'elem': document.getElementById('init'), 'po': 'before'});
        function dataInit() {
            $timeout(function() {
                if (typeof(draw) != "undefined") {
                    console.log(draw);
                    var date = new Date();
                    $scope.q = new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toJSON().slice(0,10);
                    $scope.result = draw;
                    //$scope.items = data["e70e381a-29a9-4361-ba47-bce3b2e72348"]["data"];
                    $('#refresh').text('（10秒后刷新）');
                    refresh();
                }
            }, 0);
        }
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
    var nav = document.createElement('nav');
    nav.setAttribute('class', 'navbar navbar-default navbar-fixed-top');
    $('body').prepend(nav);
    var navObj = $('body nav:first-child');
    navObj.next().css({'margin-top': navObj.height()});
    $('body > nav').append('<div class="container-fluid">');
    $('body > nav > div.container-fluid').append('<div class="navbar-header"> <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse-1" aria-expanded="true"> <span class="sr-only">Toggle navigation</span> <span class="icon-bar"></span> <span class="icon-bar"></span> <span class="icon-bar"></span> </button> <a href="javascript:void(0);" onclick="window.location.reload();" class="navbar-brand">刷新</a><a id="refresh" class="navbar-brand" style="font-size:14px; padding-left:0;" href="javascript:void(0);">（加载中...）</a> </div>').append('<div class="collapse navbar-collapse" id="bs-navbar-collapse-1"><ul class="nav navbar-nav"><li><a href="'+ (pathname.indexOf('/output.html') >= 0 ? 'record.html">抽奖记录' : 'output.html">测水记录') + '</a></li></ul></div>');
    
    $("#refresh").on('click', function(e){
        e.preventDefault();
        if (timer) {
            clearInterval(timer);
            $(this).text('（已关闭自动刷新）');
            timer = null;
        } else {
            $(this).text('（10秒后刷新）');
            timer = refresh();
        }
    });

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

function loadScript(url, callback, position) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    if(typeof(callback) != "undefined"){
        script.onload = script.onreadystatechange = function() {
            if (!script.readyState || script.readyState == "loaded" || script.readyState == "complete") {
                script.onreadystatechange = null;
                callback();
            }
        }

    }
    script.src = url;
    if(typeof(position) != "undefined") {
        var elem = position['elem'];
        switch (position['po']) {
            case "before":
                elem.parentNode.insertBefore(script, elem);
                break;
            case "after":
                insertAfter(script, elem);
                break;
            case "prepend":
                elem.insertBefore(script, elem.firstChild);
                break;
            case "append":
                elem.appendChild(script);
                break;
            default:
                document.onload = document.onreadystatechange = function() {
                    if (!document.readyState || document.readyState == "loaded" || document.readyState == "complete") {
                        document.body.appendChild(script);
                    }
                }
        }
    } else {
        document.onload = document.onreadystatechange = function() {
            if (!document.readyState || document.readyState == "loaded" || document.readyState == "complete") {
                document.body.appendChild(script);
            }
        }
    }
}

function urlParser(url) {
    var el = document.createElement('a');
    el.href = url;
    return el;
}

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function refresh() {
    timer = null;
    var time = 10;
    timer = setInterval(function() {
       time--;
       if (time == 0) {
           $('#refresh').text('（正在刷新 ...）');
           clearInterval(timer);
           document.location.reload(true);
       } else {
        $('#refresh').text('（' + time + '秒后刷新）');
       }
    }, 1000);
}