var chatApp = angular.module('chatApp', []);
chatApp.controller('chatcontroller', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');

    $scope.messages = [];
    $scope.results = [];
    $scope.rooms = [];
    $scope.name = '';
    $scope.text = '';
    $scope.user = '';
    socket.on('message', function(msg) {
        $scope.messages.push(msg);
        $scope.$apply();
        var elem = document.getElementById('msgpane');
        elem.scrollTop = elem.scrollHeight;


    });
    
    $scope.createNewRoom = function createNewRoom(){
        if($scope.user != ''){
            socket.emit('createNewRoom', $scope.user, $scope.roomname);
            $scope.roomname = '';
        }
        else{
            console.log("You must login before you can create a new room.");
        }
    };
    
    socket.on('rooms', function(msg) {
        $scope.rooms.push(msg);
        $scope.$apply();
    });
    
    socket.on('roomExists', function() {
        console.log('That room name already exists. Nothing happens');
        $scope.createRoom = '';
    });
    
    socket.on('loginChat', function(username) {
        console.log('logging in as ' + username);
        $scope.user = username;
    });
    socket.on('search', function(search) {
        console.log(search);
        $scope.results.push(search);
        $scope.$apply();
        console.log('Search');
        var elem = document.getElementById('searchpane');
        elem.scrollTop = elem.scrollHeight;


    });
    $scope.searchSend = function searchSend() {
        if ($scope.user != '') {
            socket.emit('search', $scope.search);
            $scope.search = '';
        }
        else {
            console.log("Error you must login first.");
        }
    };
    $scope.sendMessage = function sendMessage() {
        if ($scope.user != '') {
            socket.emit('chat', $scope.message, $scope.user);
            $scope.message = '';
        }
        else {
            console.log("Error you must login first.");
        }
    };

    $scope.processLogin = function processLogin() {
        socket.emit('login', $scope.password, $scope.Username);
    };

    socket.on('setuser', function(user) {
        $scope.$apply();
    });

    function login(showhide) {
        if (showhide == "show") {
            document.getElementById('popupbox').style.visibility = "visible";
        }
        else if (showhide == "hide") {
            document.getElementById('popupbox').style.visibility = "hidden";
        }
    }
    function passin(){
        socket.emit('createChat');
    }
    socket.on('connect', function() {
        passin();
    });

});