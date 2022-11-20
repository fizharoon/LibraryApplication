const xhttp = new XMLHttpRequest();
const method = "GET";  // Could be GET, POST, PUT, DELETE, etc.
const url = "http://127.0.0.1:5000"; 
const async = true;   // asynchronous (true) or synchronous (false) – don’t use synchronous

function openTask(evt, task) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(task).style.display = "block";
    evt.currentTarget.className += " active";
}

function updateTables() {
    document.getElementById("bookSearchResults").innerHTML.reload;
    document.getElementById("userSearchResults").innerHTML.reload;
}

function logout() {
    var newUrl = url + '/logout';

    xhttp.open("GET", newUrl);

    xhttp.onload = function() {
        window.location.replace('/');
    }

    xhttp.send();
}

function searchUserByName() {
    var searchParameter = document.getElementById("userSearchfield").value;
    var newUrl = url + '/usersearch?name=' + encodeURIComponent(searchParameter);
    xhttp.open("GET", newUrl)

    attributes = ['u_userkey', 'u_name', 'u_username', 'u_password', 'u_librariankey', 'u_address', 'u_phone'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        
        data.forEach(user => {
            result += "<tr>";
            attributes.forEach(attribute => {
                result += "<td>"+user[attribute]+"</td>";
            });
            result += "<td><button onClick=\"deleteUser(" + user['u_userkey'] + ")\">Delete User</button></td>";
            result += "</tr>";
        });
        document.getElementById("userSearchResults").innerHTML = result;
    }

    xhttp.send();
}

function updateUser() {
    let userkey = document.getElementById("u_userkey");
    let newUrl = url + '/updateuser/' + userkey;
    let data = {'u_name': document.getElementById("u_name"),
                'u_username': document.getElementById("u_username"),
                'u_password': document.getElementById("u_password"),
                'u_address': document.getElementById("u_address"),
                'u_phone': document.getElementById("u_phone")};
    xhttp.open('PUT', newUrl);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(data));
}

function deleteUser(userkey) {
    let newUrl = url + '/deleteuser';
    let data = {'u_userkey': userkey};
    xhttp.open('DELETE', newUrl);
    xhttp.onload = function() {
        searchUserByName();
        updateTables();
    }
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(data));
}

function createUser() {

}

function searchBooksByTitle() {
    var searchParameter = document.getElementById("bookSearchfield").value;
    var newUrl = url + '/search?keyword=' + encodeURIComponent(searchParameter);
    xhttp.open("GET", newUrl)

    attributes = ['b_title', 'b_type', 'b_availability'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";

        data.forEach(book => {
            result += "<tr>";
            result += "<td><button onClick=\"deleteBook(" + book['b_bookkey'] + ")\">Remove</button></td>";
            result += "<td><a href=\"/bookinfo/" + book['b_bookkey'] + "\">" + book['b_bookkey'] + "</a></td>";
            attributes.forEach(attribute => {
                result += "<td>"+book[attribute]+"</td>";
            });
            result += "</tr>";
        });

        document.getElementById("bookSearchResults").innerHTML = result;
        document.getElementById("searchResCount").innerHTML = data.length + ' results';
    }

    xhttp.send();
}

function updateBook() {

}

function deleteBook(bookkey) {
    let newUrl = url + '/deletebook';
    let body = {'b_bookkey': bookkey};
    xhttp.open('DELETE', newUrl);
    xhttp.onload = function() {
        searchBooksByTitle();
        updateTables();
    }
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(body));
}

function createBook() {

}

function getBook(bookkey) {
    var newUrl = url + '/bookinfo/' + bookkey;
    xhttp.open('GET', newUrl);
    xhttp.onload = function() {
        // console.log(this.response);
    }
    xhttp.send();
}