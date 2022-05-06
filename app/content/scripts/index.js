let na;

function init() {
    na = new NoAPI('ws://' + window.location.hostname + '/ws');
    na.onmessage = (msg) => logMessage('INFO ' + msg);

    na.register('jsthing1', jsThing1);
    na.register('jsthing2', jsThing2);

    document.querySelector("#thing1-button").addEventListener("click", pyThing1, false);
    document.querySelector("#thing2-button").addEventListener("click", pyThing2, false);
}

function logMessage(msg) {
    let log = document.querySelector("#log-box");
    log.innerHTML = log.innerHTML + msg + "\n";
    log.scrollTop = log.scrollHeight;
}

function pyThing1() {
    na.call('pything1', 'a').then((ret) => {
        logMessage("pyThing1('a') = " + ret);
    });
}

function pyThing2() {
    na.call('pything2', 'b').then((ret) => {
        logMessage("pyThing2('b') = " + ret);
    });
}

function jsThing1(data) {
    logMessage("running jsThing1(" + data + ")");
    return "Data: " + data;
}

async function jsThing2(data) {
    logMessage("running jsThing2(" + data + ")");
    na.info("Waiting...");
    await new Promise(r => setTimeout(r, 2000));
    return "Data: " + data;
}

function sendMSG() {
    let msg = document.querySelector("#msg-box").value;
    na.info(msg);
}

window.addEventListener("load", init, false);
