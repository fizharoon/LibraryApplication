const xhttp = new XMLHttpRequest();
const method = "GET";  // Could be GET, POST, PUT, DELETE, etc.
const url = "http://127.0.0.1:5000"; 
const async = true;   // asynchronous (true) or synchronous (false) – don’t use synchronous

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