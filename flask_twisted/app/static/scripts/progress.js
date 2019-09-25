window.onload = function() {
    var generator_id = window.location.href.split("/").pop()
    var dataPath = window.location.protocol + "//" + window.location.host + "/"
    console.log(dataPath);

    var interval = setInterval(updateProgress, 1000);

    function updateProgress() {
        const req = new XMLHttpRequest();
        req.open('GET', dataPath + 'status/' + generator_id, false);
        req.send(null);

        var progress = JSON.parse(req.response);

        if (progress['crawling'] === true) {
            // if we get the temporary JSON just pass the
        }

        else {
            if (progress['url_crawled'] === progress['url_total']) {
                stopProgress(interval);
            }
            else {
                displayProgress(progress['url_crawled'], progress['url_total'])
            }
        }
    }

    function displayProgress(crawled, total) {
        var container = document.getElementById('progress')
        container.textContent = ''
        var textNode = document.createTextNode(crawled + " URL crawled out of " + total + " total")
        container.appendChild(textNode);
    }

    function stopProgress(interval) {
        clearInterval(interval);
        setInterval(function() {

        })
        document.location.reload();
    }

    function writeRedirectMessage() {

    }

}
