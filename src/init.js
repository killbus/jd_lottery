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