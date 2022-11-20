const xhttp = new XMLHttpRequest();
const method = "GET";  // Could be GET, POST, PUT, DELETE, etc.
const url = "http://127.0.0.1:5000"; 
const async = true;   // asynchronous (true) or synchronous (false) – don’t use synchronous


// Get the input field
var input = document.getElementById("password");

input.addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    document.getElementById("loginbutton").click();
  }
});

function updateTables() {
    document.getElementById("searchResults").innerHTML.reload;
    document.getElementById("checkoutTable").innerHTML.reload;
    document.getElementById("holdTable").innerHTML.reload;
}


function login() {
    var newUrl = url + '/login';
    var data = {"username": document.getElementById("username").value,
                "password": document.getElementById("password").value};
    xhttp.open("POST", newUrl);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function() {
        user = JSON.parse(this.response);
        if (user[0].length === 7) {
            window.location.href = url + "/user";
        } else {
            window.location.href = url + "/librarian";
        }
    }
    xhttp.send(JSON.stringify(data));
}

function logout() {
    var newUrl = url + '/logout';

    xhttp.open("POST", newUrl, true);

    xhttp.onload = function() {
        window.location.replace('/');
    }

    xhttp.send();
}

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

function searchBooksByTitle() {
    var searchParameter = document.getElementById("searchfield").value;
    var newUrl = url + '/search'  + '?keyword=' + encodeURIComponent(searchParameter);
    xhttp.open("GET", newUrl)

    attributes = ['b_title', 'b_pages', 'b_rating', 'b_type', 'b_availability'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        
        data.forEach(book => {
            result += "<tr>";
            if (book['b_availability'] == 'Available') {
                if (book['isCheckedOut']) {
                    result += "<td>Checked Out</button></td>"
                } else {
                    result += "<td><button onClick=\"checkOut(" + book['b_bookkey'] + ")\">Check Out</button></td>"
                }
            } else {
                if (book['isHeld']) {
                    result += "<td>Held</button></td>"
                } else if (book['isCheckedOut']) {
                    result += "<td>Checked Out</button></td>"
                } else {
                    result += "<td><button onClick=\"placeHold(" + book['b_bookkey'] + ")\">Place Hold</button></td>"
                }
            }
            attributes.forEach(attribute => {
                result += "<td>"+book[attribute]+"</td>";
            });
            
            result += "</tr>";
        });
        document.getElementById("searchResults").innerHTML = result;
        document.getElementById("searchResCount").innerHTML = data.length + ' results';
    }

    xhttp.send();
}

function currentCheckouts() {
    var newUrl = url + '/usercheckouts';
    xhttp.open("GET", newUrl)

    attributes = ['b_title', 'b_format', 'b_checkout'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        
        data.forEach(book => {
            result += "<tr>";
            
            attributes.forEach(attribute => {
                result += "<td>"+book[attribute]+"</td>";
            });

            if (book['b_remaining'] == 'n/a')
                result += "<td><button onClick=\"returnBook(" + book['b_bookkey'] + ")\">Return</button></td>";
            else
                result += "<td>" + book['b_remaining'] + " days remaining</td>"
            
            result += "</tr>";
        });
        document.getElementById("checkoutTable").innerHTML = result;
    }

    xhttp.send();
}

function currentHolds() {
    var newUrl = url + '/userholds';
    xhttp.open("GET", newUrl)

    attributes = ['b_title', 'h_holdplaced', 'availability'];

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        
        data.forEach(book => {
            result += "<tr>";
            if (book['availability'] == 'Available') {
                result += "<td><button onClick=\"checkOut(" + book['b_bookkey'] + ")\">Check Out</button></td>";
            } else {
                result += "<td></td>";
            }
            attributes.forEach(attribute => {
                result += "<td>"+book[attribute]+"</td>";
            });
            
            result += "</tr>";
        });
        document.getElementById("holdTable").innerHTML = result;
    }

    xhttp.send();
}

function checkOut(bookkey) {
    var newUrl = url + '/checkout';
    var body = {'bookkey': bookkey};
    xhttp.open('POST', newUrl);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function() {
        searchBooksByTitle();
        updateTables();
    }
    xhttp.send(JSON.stringify(body));
}

function returnBook(bookkey) {
    var newUrl = url + '/return';
    var body = {'bookkey': bookkey};
    xhttp.open('POST', newUrl);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function() {
        currentCheckouts();
        updateTables();
    }
    xhttp.send(JSON.stringify(body));
}

function placeHold(bookkey) {
    var newUrl = url + '/hold';
    var body = {'bookkey': bookkey};
    xhttp.open('POST', newUrl);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function() {
        searchBooksByTitle();
        updateTables();
    }
    xhttp.send(JSON.stringify(body))
    
}