async function sendMessage() {
    let input = document.getElementById("input");
    let msg = input.value;

    if (!msg) return;

    addMessage(msg, "user");

    let res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: msg})
    });

    let data = await res.json();

    addMessage(data.answer, "bot");

    input.value = "";
}

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    document.getElementById("messages").appendChild(div);
}
