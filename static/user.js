const xhttp = new XMLHttpRequest();
const method = "GET";  // Could be GET, POST, PUT, DELETE, etc.
const url = "http://127.0.0.1:5000"; 
const async = true;   // asynchronous (true) or synchronous (false) – don’t use synchronous


// async function getStudent() {
//     var studentName = document.getElementById("studentNameSearch").value;
//     var newUrl = url + "/" + studentName;
//     xhttp.open("GET", newUrl, true);
    
//     xhttp.onload = function() {
//       data = JSON.parse(this.response);
//       document.getElementById("studentGradeSearch").value = data[studentName];
//     };
//     // console.log(data[studentName.value]);
//     xhttp.send();
  
//   }

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

// function printAll(){
//     xhttp.open("GET", url, async);
//     xhttp.onload = function() {
//       // document.getElementById("demo").innerHTML = this.responseText;
//       data = JSON.parse(this.response)
//       var table = document.getElementById("table")
//       table.innerHTML = "";
//       for (i in Object.keys(data)) {
//         // console.log(Object.keys(data)[i] + " " + data[Object.keys(data)[i]])
//         var row = table.insertRow();
//         var celluno = row.insertCell(0);
//         var celldos = row.insertCell(1);
//         celluno.innerHTML = Object.keys(data)[i];
//         celldos.innerHTML = data[Object.keys(data)[i]];
  
//       }
//       document.getElementById("print").innerHTML = "Update All";
//       // console.log(this.response);
//     };
//     // console.log(data)
//     xhttp.send();
    
//   }
function searchBooksByTitle() {
    var searchParameter = document.getElementById("searchfield").value;
    var newUrl = url + '/search/' + searchParameter;
    xhttp.open("GET", newUrl)

    xhttp.onload = function() {
        data = JSON.parse(this.response);
        var result = "";
        for (i in data) {
            result += "<tr>";
            for(j in data[i]){
                result += "<td>"+data[i][j]+"</td>";
            }
            if (data[i][data[i].length - 1] == 'Available') {
                result += "<td><button>Check Out</button></td>"
            } else {
                result += "<td><button>Place Hold</button></td>"
            }
            
            result += "</tr>";
        }
        document.getElementById("searchResults").innerHTML = result;
    }

    xhttp.send();
}

function currentHolds() {
    var holds = document.getElementById("")

}

function currentCheckouts() {

}