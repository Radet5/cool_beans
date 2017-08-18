var nameList = document.querySelector('.nameList');
var nameField = document.querySelector('.nameField');
var output = document.querySelector('.test');
 nameField.focus()

function clearList(list) {
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }
};

window.addEventListener("load", function() {
    var searchSocket = new WebSocket("ws://192.168.0.6:8080/ws0");
    var custdataSocket = new WebSocket("ws://192.168.0.6:8080/ws1");

    searchSocket.onmessage = function (event) {
        var data = JSON.parse(event.data);
        clearList(nameList)
        clearList(output)
        for (i = 0; i < data.length; i++) {
            var li = document.createElement("li");
            var last = data[i]['cust_last_name'];
            last = last.charAt(0).toUpperCase() + last.substring(1);
            var first = data[i]['cust_first_name'];
            first = first.charAt(0).toUpperCase() + first.substring(1);
            var text = last + ", " + first;
            li.appendChild(document.createTextNode(text));
            li.id = data[i]['cust_id'];
            nameList.appendChild(li);
        }
        nameList.addEventListener('click', function (e){
            var myHeading = document.querySelector('h1');
            var heading = "Safai Bean Club"
            heading = e.target.innerText;
            myHeading.textContent = heading;

            custdataSocket.send(e.target.id);
        })
    };

    custdataSocket.onmessage = function (event) {
        clearList(nameList)
        clearList(output)

        var newDiv = document.createElement("div");
        newDiv.id = "customerData";
        newDiv.innerHTML = "test<br><br>did work?";
        output.appendChild(newDiv);

    };


    nameField.addEventListener('input', function (e) {
        input_text = nameField.value;
        searchSocket.send(input_text);
        e.preventDefault();
    })
});
