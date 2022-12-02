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

    attributes = ['u_userkey', 'u_name', 'u_username', 'u_password', 'u_librariankey', 'u_address', 'u_phone', 'u_pastcheckouts', 'u_curcheckouts', 'u_curholds'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        
        data.forEach(user => {
            result += "<tr>";
            attributes.forEach(attribute => {
                result += "<td>"+user[attribute]+"</td>";
            });
            result += "<td><button onClick=\"deleteUser(" + user['u_userkey'] + ")\" class=\"chold\">Delete User</button></td>";
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
    let newUrl = url + '/createuser';
    let data = {
        "u_name": document.getElementById("u_name").value,
        "u_username": document.getElementById("u_username").value,
        "u_password": document.getElementById("u_password").value,
        "u_address": document.getElementById("u_address").value,
        "u_phone": document.getElementById("u_phone").value
    }

    xhttp.open("POST", newUrl);
    xhttp.onload = function() {
        document.getElementById("u_name").value = "";
        document.getElementById("u_username").value = "";
        document.getElementById("u_password").value = "";
        document.getElementById("u_address").value = "";
        document.getElementById("u_phone").value = "";
    }

    for (key in data) {
        if (data[key] === '')
            return 400
    }

    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(data));
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
            result += "<td><button onClick=\"deleteBook(" + book['b_bookkey'] + ")\"class=\"chold\">Remove</button></td>";
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

function createEBook() {
    let newUrl = url + '/addebook';
    let data = {
        "b_title": document.getElementById("eb_title").value,
        "b_pages": document.getElementById("eb_pages").value,
        "bs_rating": document.getElementById("ebs_rating").value,
        "bs_reviews": document.getElementById("ebs_reviews").value,
        "bs_price": document.getElementById("ebs_price").value,
        "e_format": document.getElementById("e_format").value,
        "e_loanperiod": document.getElementById("e_loanperiod").value
    }

    xhttp.open("POST", newUrl);
    xhttp.onload = function() {
        document.getElementById("eb_title").value = "";
        document.getElementById("eb_pages").value = "";
        document.getElementById("ebs_rating").value = "";
        document.getElementById("ebs_reviews").value = "";
        document.getElementById("ebs_price").value = "";
        document.getElementById("e_format").value = "";
        document.getElementById("e_loanperiod").value = "";
    }

    // for (key in data) {
    //     if (data[key] === '')
    //         return 400
    // }

    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(data));
}

function createHardcopyBook() {
    let newUrl = url + '/addhardcopybook';
    let data = {
        "b_title": document.getElementById("hb_title").value,
        "b_pages": document.getElementById("hb_pages").value,
        "bs_rating": document.getElementById("hbs_rating").value,
        "bs_reviews": document.getElementById("hbs_reviews").value,
        "bs_price": document.getElementById("hbs_price").value,
        "hb_type": document.getElementById("hb_type").value
    }

    xhttp.open("POST", newUrl);
    xhttp.onload = function() {
        document.getElementById("hb_title").value = "";
        document.getElementById("hb_pages").value = "";
        document.getElementById("hbs_rating").value = "";
        document.getElementById("hbs_reviews").value = "";
        document.getElementById("hbs_price").value = "";
        document.getElementById("hb_type").value = "";
    }

    // for (key in data) {
    //     if (data[key] === '')
    //         return 400
    // }

    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(data));
}

function getBook(bookkey) {
    var newUrl = url + '/bookinfo/' + bookkey;
    xhttp.open('GET', newUrl);
    xhttp.onload = function() {
        // console.log(this.response);
    }
    xhttp.send();
}