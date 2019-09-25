window.onload = function() {
    var generator_id = window.location.href.split("/").pop()
    var dataPath = window.location.protocol + "//" + window.location.host + "/"
    console.log(dataPath);

    const req = new XMLHttpRequest();
    req.open('GET', dataPath + 'data/' + generator_id, false);
    req.onload = function() {
        addButtonActions(req.response);
        addCopyAction(req.response);
        renderPage(req.response);
        console.log('rendering page');
    };

    req.send(null);
    addFlagAnimation();
    console.log('end');
}

function renderPage (response) {
    var data = JSON.parse(response);
    buildCspTab(response, 'raw');
    flags = data['flags'];
    insertFlag(flags);
}

function insertFlag (flagList) {
    console.log('inserting child into node')
    console.log(flagList);
    var divFlags = document.getElementById('flags')
    console.log(divFlags);
    var previousFlagUrl = '';
    for (var i = 0; i < flagList.length; i++) {
        if (previousFlagUrl !== flagList[i]['url']) {
            var titleUrl = document.createTextNode(flagList[i]['url']);
            var titleParagraph = document.createElement('h4')
            var hr = document.createElement('hr')

            titleParagraph.appendChild(titleUrl);
            titleParagraph.appendChild(hr);

            divFlags.appendChild(titleParagraph);

            previousFlagUrl = flagList[i]['url'];
        }
        var child = buildFlag(flagList[i], divFlags);
        console.log('child');
        console.log(child);
        for (var j = 0; j < child.length; j++) {
            divFlags.appendChild(child[j]);
        }
    }
}


function buildFlag(flag) {
    console.log('building flag');

    var button = document.createElement('button');
    var node = document.createTextNode(flag['description']);
    button.appendChild(node);
    button.classList.add('collapsible')

    var div = document.createElement('div');
    div.classList.add('content');

    var paragraph = buildFlagContent('Content', flag['content']);
    div.appendChild(paragraph);

    var paragraph = buildFlagContent('Location', flag['location']);
    div.appendChild(paragraph)

//    var paragraph = buildFlagContent('For the page', flag['url']);
//    div.appendChild(paragraph);

    var paragraph = buildFlagContent('Recommendation' , flag['reco']);
    div.appendChild(paragraph);

    return [button, div];
}

function buildFlagContent(label, content) {
    var paragraph = document.createElement('p');
    paragraph.classList.add('content-paragraph');

//    var hr = document.createElement('hr');
//    paragraph.appendChild(hr);

    var span = document.createElement('span');
    var span_content = document.createTextNode(label);
    span.appendChild(span_content);

    var subparagraph = document.createElement('p')
    var node = document.createTextNode(content);

    subparagraph.classList.add('right-content')
    subparagraph.appendChild(node);

    paragraph.appendChild(span);
    paragraph.appendChild(subparagraph);

//    var hr = document.createElement('hr');
//    paragraph.appendChild(hr);

    console.log(paragraph);
    return paragraph;
}

function buildCspTab(response, id) {
    console.log('starting building csp tab');
    console.log(id);
    var csp_tab = document.getElementById('csp-tab');
    while (csp_tab.firstChild) {
        console.log('removing child');
        console.log(csp_tab.firstChild)
        csp_tab.removeChild(csp_tab.firstChild);
    }
    var table = document.createElement('table');

    var data = JSON.parse(response);

    if (id === 'raw') {
        var csp_data = data['csp-raw'];
    }
    else if (id === 'directory-simplified') {
        var csp_data = data['csp-directory-simplified'];
    }
    else if (id === 'self-simplified') {
        var csp_data = data['csp-self-simplified'];
    }
    else if (id === 'fully-simplified') {
        var csp_data = data['csp-fully-simplified'];
    }
    else {
        var csp_data = data['csp-raw'];
    }

    console.log(csp_data);

    addingTableHeaders(table);

    for (key in csp_data) {
        var directive_tr = document.createElement('tr');
        var directive_td = document.createElement('td');
        var tr_text = document.createTextNode(key);

        // building structure of basic node
        directive_td.appendChild(tr_text);
        directive_tr.appendChild(directive_td);

        // build all the sources node
        sources = csp_data[key].join(' ');
        var source_td = document.createElement('td');
        var tr_text = document.createTextNode(sources);

        // append source for the
        source_td.appendChild(tr_text);
        directive_tr.appendChild(source_td);


        // building title of the tab
        // append the result to the tab
        table.appendChild(directive_tr);
    }

    table.classList.add('csp-table')
    csp_tab.appendChild(table)
}


function addingTableHeaders(table) {
    // Function that adds Sources and Directives Headers to given table
    var tab_headers = document.createElement('tr');
    var directive_th = document.createElement('th');
    var sources_th = document.createElement('th');

    var directive_text = document.createTextNode('Directives');
    var sources_text = document.createTextNode('Sources');

    directive_th.append(directive_text);
    sources_th.appendChild(sources_text);

    tab_headers.appendChild(directive_th);
    tab_headers.appendChild(sources_th);

    table.appendChild(tab_headers);

}

function addFlagAnimation() {
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
        }
      });
    }
}

function addButtonActions (response) {
    var inputs = document.getElementsByTagName('input');
    console.log(inputs);
    for (var i = 0; i < inputs.length; i++) {
        var value = inputs[i].value;
        console.log("Adding listener to " + inputs[i] + " with value " + value);
        console.log(value);
        inputs[i].onclick = function (){
            buildCspTab(response, this.value)
            warningParagraph = document.getElementById('simplification')
            warningParagraph.textContent = ''
            if (this.value == 'directory-simplified'){
                var textNode = document.createTextNode('Warning ! You used directory simplifications. This may lead to security issues if one of the simplified directories sources contains malicious content (uploads from user for example).')
                warningParagraph.appendChild(textNode)
            }

            else if (this.value == 'self-simplified'){
                var textNode = document.createTextNode('Warning ! You used self simplification. This may lead to security issues if your domain contains malicious content (uploads from user for example).')
                warningParagraph.appendChild(textNode)
            }

            else if (this.value == 'fully-simplified'){
                var textNode = document.createTextNode('Warning ! You fully simplified the generated CSP. This may lead to security issues if your domain contains of simplified directories source contains malicious content (uploads from user for example).')
                warningParagraph.appendChild(textNode)
            }
        }
    }
}

function addWarningParagraph () {

}

function addCopyAction (response) {
    var button = document.getElementById('csp-copy');
    var radio_div = document.getElementById('csp-options')
    var radios = radio_div.getElementsByTagName('input')

    button.onclick = function () {
        for (var i=0; i < radios.length; i++) {
            if (radios[i].checked) {
                console.log(radios[i].value);
                var data = JSON.parse(response);
                navigator.clipboard.writeText(data['header'][radios[i].value]);
            }
        }
    }
}
