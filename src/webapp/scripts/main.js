var nameList = document.querySelector('.nameList');
var nameField = document.getElementById('nameField');
var output = document.getElementById('output');
var searchDiv = document.getElementById('search_div');
nameField.focus();

function clearList(list) {
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }
};

function sendToServer(socket, json_text, console) {

        if (socket.readyState == socket.OPEN) {
                socket.send(json_text);
        }
        else {
            clearList(console);
            var msg = document.createElement("h2");
            var subtext = document.createElement("div");
            msg.textContent = "Connection Error:";
            subtext.innerHTML = "<p>Socket is not open</p>";
            console.appendChild(msg);
            console.appendChild(subtext);
        }
}

function createRadioList(div, data, name, ids_key, labels_key) {
   for (i = 0; i < data.length; i++) {
       var radio = document.createElement("input");
       radio.setAttribute("type", "radio");
       radio.name = name;
       radio.value = data[i][ids_key];
       radio.id = data[i][labels_key];
       div.appendChild(radio);
       var label = document.createElement("label");
       label.setAttribute("for",data[i][labels_key]);
       label.textContent = data[i][labels_key];
       div.appendChild(label);
       div.appendChild(document.createElement("br"));
   }

};

window.addEventListener("load", function() {
    var ip = self.location.host
//  var ip = "127.0.0.1"
    var webSocketString = "ws://" + ip + "/ws0";
    var searchSocket = new WebSocket(webSocketString);

    nameField.addEventListener('input', function (e) {
        input_text = nameField.value;
        json_text = "{\"type\":0, \"data\":\"" + input_text + "\"}";
        sendToServer(searchSocket, json_text, output);
        e.preventDefault();
    })

    var registerButtonDiv = document.createElement("div");
    registerButtonDiv.id = "registerCustomer";
    registerButtonDiv.className = "button";
    registerButtonDiv.innerHTML = "&nbspAdd Customer&nbsp";
    registerButtonDiv.addEventListener('click', function (e) {
        clearList(output);
        clearList(nameList);
        searchDiv.removeChild(registerButtonDiv);
        var firstNameField = document.createElement("input");
        firstNameField.id = "firstNameField";
        firstNameField.className = "nameField";
        firstNameField.type = "text";
        firstNameField.placeholder = "First Name";
        var lastNameField = document.createElement("input");
        lastNameField.id = "lastNameField";
        lastNameField.className = "nameField";
        lastNameField.type = "text";
        lastNameField.placeholder = "Last Name";
        lastNameField.value = nameField.value;
        var submitCust = document.createElement("div");
        submitCust.id = "cust_submit_button";
        submitCust.className = "button";
        submitCust.innerHTML = "&nbspSubmit&nbsp";
        submitCust.addEventListener('click', function (e) {
            if (firstNameField.value != "" && lastNameField.value != "") {
                submitCust.textContent = "GOOD";
                json_text = "{\"type\":3, \"data\":{\"last_name\":\""+lastNameField.value+"\",\"first_name\":\""+firstNameField.value+"\"}}";
        //After all said and done, put stuff back
                searchDiv.appendChild(nameField);
                searchDiv.appendChild(nameList);
                searchDiv.removeChild(firstNameField);
                searchDiv.removeChild(lastNameField);
                searchDiv.removeChild(submitCust);
                searchDiv.removeChild(backButtonDiv);
                searchDiv.appendChild(registerButtonDiv);
                nameField.focus();
                sendToServer(searchSocket, json_text, output);
            }
            else {
                alert("Please enter a first and a last name");
            }
        });

        var backButtonDiv = document.createElement("div");
        backButtonDiv.id = "back";
        backButtonDiv.className = "button";
        backButtonDiv.innerHTML = "&nbspBack&nbsp";
        backButtonDiv.addEventListener('click', function (e) {
            input_text = lastNameField.value;
            json_text = "{\"type\":0, \"data\":\"" + input_text + "\"}";
            searchDiv.appendChild(nameField);
            searchDiv.appendChild(nameList);
            searchDiv.removeChild(firstNameField);
            searchDiv.removeChild(lastNameField);
            searchDiv.removeChild(submitCust);
            searchDiv.removeChild(backButtonDiv);
            searchDiv.appendChild(registerButtonDiv);
            nameField.focus();
            sendToServer(searchSocket, json_text, output);
            e.preventDefault();
        });
       
        searchDiv.removeChild(nameField);
        searchDiv.removeChild(nameList);
        searchDiv.appendChild(firstNameField);
        searchDiv.appendChild(lastNameField);
        searchDiv.appendChild(submitCust);
        searchDiv.appendChild(backButtonDiv);
        lastNameField.focus();
        
    });

    searchDiv.appendChild(registerButtonDiv);
    

    searchSocket.onmessage = function (event) {
        var json_data = JSON.parse(event.data);
        var myHeading = document.getElementById('heading');
        var heading = "Safai Bean Club";
        switch (json_data['type']) {
            case 0:
                nameField.focus();
                heading = "Safai Bean Club";
                myHeading.textContent = heading;
                data = json_data['data'];
                clearList(nameList);
                clearList(output);
                var hasChild = searchDiv.querySelector("#registerCustomer") != null;
                if (!hasChild) {
                    searchDiv.appendChild(registerButtonDiv);
                }

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
                    if (e.target.id) {
                        json_text = "{\"type\":1, \"data\":" + e.target.id +"}";
                        sendToServer(searchSocket, json_text, output);
                    }
                });
                break;
            case 1:
                clearList(nameList);
                clearList(output);
                var hasChild = searchDiv.querySelector("#registerCustomer") != null;
                if (hasChild) {
                    searchDiv.removeChild(registerButtonDiv);
                }
//              nameField.focus();

                var data = json_data['data']

                
                var last = data['lastName'].charAt(0).toUpperCase() + data['lastName'].substring(1);
                var first = data['firstName'].charAt(0).toUpperCase() + data['firstName'].substring(1);
                heading =  last + ", " + first;
                myHeading.textContent = heading;

                var custDiv = document.createElement("div");
                var tableElement = document.createElement("table");
                custDiv.id = "custData";
                purchases = data['custData'];
                if (purchases.length == 0) {
                    custDiv.appendChild(document.createTextNode("No Purchases"));
                }
                else {
                    html =  "<thead><tr><th>Coffee Name</th><th>Grind</th>";
                    html += "<th>Weight</th><th>Transaction Date</th><th>Type</th></tr></thead>";
                    html += "<tbody>";
                    for (i = 0; i < purchases.length; i++) {
//                      dt_str = purchases[i]['purchase_date']+" UTC";
//                      var date = new Date(dt_str);
//                      var options = {hour:'2-digit', minute:'2-digit'};
//                      purch_date = date.toLocaleDateString('en-US', options);
                        html += "<tr>";
                        html += "<td>" + purchases[i]['coffee_name'] + "</td>";
                        html += "<td>" + purchases[i]['grind_desc'] + "</td>";
                        html += "<td>" + purchases[i]['purchase_weight'] + "oz</td>";
                        html += "<td>" + purchases[i]['purchase_date'] + "</td>";
                        html += "<td>" + purchases[i]['type'] + "</td>";
                        html += "</tr>";
                    }
                    html += "</tbody>";
                    tableElement.innerHTML = html;
                    var claimButton = document.createElement("div");
                    claimButton.id="claimButton" ;
                    claimButton.className="button";
                    claimButton.innerHTML = "&nbspClaim free bag!&nbsp";
                    claimButton.addEventListener('click', function (e) {
    //                  output.removeChild(addButtonDiv);
                        clearList(output);

                        var backButtonDiv = document.createElement("div");
                        backButtonDiv.id = "back";
                        backButtonDiv.className = "button";
                        backButtonDiv.innerHTML = "&nbspBack&nbsp";
                        backButtonDiv.addEventListener('click', function (e) {
                            json_text = "{\"type\":1, \"data\":" + data['custId'] +"}";
                            sendToServer(searchSocket, json_text, output);
                        });

                        var coffees = document.createElement("div");
                        coffees.id = "coffees";
                        var h2 = document.createElement("h2");
                        h2.textContent = "Coffee Type";
                        coffees.appendChild(h2);
                        createRadioList(coffees, data['coffeeData'], 'coffee', 'coffee_id', 'coffee_name');
                        output.appendChild(coffees);
            
                        var grinds = document.createElement("div");
                        grinds.id = "grinds";
                        h2 = document.createElement("h2")
                        h2.textContent = "Grind Type"
                        grinds.appendChild(h2);
                        createRadioList(grinds, data['grindData'], 'grind', 'grind_id', 'grind_desc');
                        output.appendChild(grinds);

                        var weightData = JSON.parse("[{\"weight_val\":16, \"weight_desc\":\"16oz\"},{\"weight_val\":12, \"weight_desc\":\"12oz\"},{\"weight_val\":8, \"weight_desc\":\"8oz\"},{\"weight_val\":0, \"weight_desc\":\"See Notes\"}]");
                        var weights = document.createElement("div");
                        weights.id = "weights";
                        h2 = document.createElement("h2");
                        h2.textContent = "Weight";
                        weights.appendChild(h2);
                        createRadioList(weights, weightData, 'weight', 'weight_val', 'weight_desc');
                        output.appendChild(weights);

                        var submit = document.createElement("div");
                        submit.id = "submit_button";
                        submit.className = "button";
                        submit.innerHTML = "&nbspSubmit&nbsp";
                        submit.addEventListener('click', function (e) {
                            var sel_coffee = "";
                            var sel_grind = "";
                            var sel_weight = "";
                            if (document.querySelector('input[name="coffee"]:checked') &&  document.querySelector('input[name="grind"]:checked') &&  document.querySelector('input[name="weight"]:checked')) {
                                submit.textContent = "GOOD";
                                sel_coffee = document.querySelector('input[name="coffee"]:checked').value;
                                sel_grind = document.querySelector('input[name="grind"]:checked').value;
                                sel_weight = document.querySelector('input[name="weight"]:checked').value;

                                json_text = "{\"type\":4, \"data\":{\"cust_id\":"+data['custId']+", \"coffee_id\":"+sel_coffee+", \"grind_id\":"+sel_grind+", \"weight\":"+sel_weight+"}}"
                                sendToServer(searchSocket, json_text, output);
                            }
                            else {
                                alert("Please select all options <3");
                            }
                            
                        });

                        output.appendChild(submit);
                        output.appendChild(backButtonDiv);
                    });
                    var notes = document.createElement("input");
                    notes.id = "notesField";
                    notes.className = "notesField";
                    notes.type = "text";
                    notes.value = data['notes'];
                    if (notes.value.length > 0) {
                        notes.size = notes.value.length;
                    }
                    else {
                        notes.size = 20;
                    }
                    notes.addEventListener('input', function (e) {
                        notes_text = notes.value;
                        json_text = "{\"type\":5, \"data\":{\"cust_id\":"+data['custId']+", \"cust_notes\":\""+notes_text+"\"}}";
                        sendToServer(searchSocket, json_text, output);
                        e.preventDefault();
                    })
                    custDiv.appendChild(notes);
                    var announce = document.createElement("p");
                    announce.innerHTML = data['remainingPurch'].toString() +" purchases until next free bag";
                    if (data['remainingRewards'] > 0) {
                        announce.innerHTML += "<br>"+data['remainingRewards'].toString() +" free bags earned";
                        custDiv.appendChild(announce);
                        custDiv.appendChild(claimButton);
                    }
                    else {
                        custDiv.appendChild(announce);
                    }
                    custDiv.appendChild(tableElement);
                }


                var addButtonDiv = document.createElement("div");
                addButtonDiv.id = "addPurchase";
                addButtonDiv.className = "button";
                addButtonDiv.innerHTML = "&nbspAdd Purchase&nbsp";
                addButtonDiv.addEventListener('click', function (e) {
//                  output.removeChild(addButtonDiv);
                    clearList(output);

                    var backButtonDiv = document.createElement("div");
                    backButtonDiv.id = "back";
                    backButtonDiv.className = "button";
                    backButtonDiv.innerHTML = "&nbspBack&nbsp";
                    backButtonDiv.addEventListener('click', function (e) {
                        json_text = "{\"type\":1, \"data\":" + data['custId'] +"}";
                        sendToServer(searchSocket, json_text, output);
                    });

                    var coffees = document.createElement("div");
                    coffees.id = "coffees";
                    var h2 = document.createElement("h2");
                    h2.textContent = "Coffee Type";
                    coffees.appendChild(h2);
                    createRadioList(coffees, data['coffeeData'], 'coffee', 'coffee_id', 'coffee_name');
                    output.appendChild(coffees);
            
                    var grinds = document.createElement("div");
                    grinds.id = "grinds";
                    h2 = document.createElement("h2")
                    h2.textContent = "Grind Type"
                    grinds.appendChild(h2);
                    createRadioList(grinds, data['grindData'], 'grind', 'grind_id', 'grind_desc');
                    output.appendChild(grinds);

                    var weightData = JSON.parse("[{\"weight_val\":16, \"weight_desc\":\"16oz\"},{\"weight_val\":12, \"weight_desc\":\"12oz\"},{\"weight_val\":8, \"weight_desc\":\"8oz\"},{\"weight_val\":0, \"weight_desc\":\"See Notes\"}]");
                    var weights = document.createElement("div");
                    weights.id = "weights";
                    h2 = document.createElement("h2");
                    h2.textContent = "Weight";
                    weights.appendChild(h2);
                    createRadioList(weights, weightData, 'weight', 'weight_val', 'weight_desc');
                    output.appendChild(weights);

                    var submit = document.createElement("div");
                    submit.id = "submit_button";
                    submit.className = "button";
                    submit.innerHTML = "&nbspSubmit&nbsp";
                    submit.addEventListener('click', function (e) {
                        var sel_coffee = "";
                        var sel_grind = "";
                        var sel_weight = "";
                        if (document.querySelector('input[name="coffee"]:checked') &&  document.querySelector('input[name="grind"]:checked') &&  document.querySelector('input[name="weight"]:checked')) {
                            submit.textContent = "GOOD";
                            sel_coffee = document.querySelector('input[name="coffee"]:checked').value;
                            sel_grind = document.querySelector('input[name="grind"]:checked').value;
                            sel_weight = document.querySelector('input[name="weight"]:checked').value;

                            json_text = "{\"type\":2, \"data\":{\"cust_id\":"+data['custId']+", \"coffee_id\":"+sel_coffee+", \"grind_id\":"+sel_grind+", \"weight\":"+sel_weight+"}}"
                            sendToServer(searchSocket, json_text, output);
                        }
                        else {
                            alert("Please select all options <3");
                        }
                        
                    });

                    output.appendChild(submit);
                    output.appendChild(backButtonDiv);

                });

                var backButtonDiv = document.createElement("div");
                backButtonDiv.id = "back";
                backButtonDiv.className = "button";
                backButtonDiv.innerHTML = "&nbspBack&nbsp";
                backButtonDiv.addEventListener('click', function (e) {
                    input_text = nameField.value;
                    json_text = "{\"type\":0, \"data\":\"" + input_text + "\"}";
                    sendToServer(searchSocket, json_text, output);
                    e.preventDefault();
                });
                output.appendChild(addButtonDiv);
                output.appendChild(backButtonDiv);
                output.appendChild(custDiv);
                notes.focus();
                break;
            case -1:
                if (json_data['data'].length > 0) {
                    alert(json_data['data'][0]);
                }
                else {
                    alert("Server Error");
                }
                break;
            case -2:
                alert(json_data['data']);
                json_text = "{\"type\":1, \"data\":" + json_data['cust_id'] + "}";
                sendToServer(searchSocket, json_text, output);
                break;
        }
    };


});
