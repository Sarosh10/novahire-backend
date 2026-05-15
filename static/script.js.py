function startListening() {

try {

const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

if (!SpeechRecognition) {

alert("Speech Recognition not supported");

return;

}

const recognition = new SpeechRecognition();

recognition.lang = 'en-US';

recognition.start();

recognition.onstart = function () {

alert("Mic Started. Speak Now.");

};

recognition.onresult = function (event) {

const text = event.results[0][0].transcript;

document.getElementById("answer").value = text;

};

recognition.onerror = function (event) {

alert("Voice Error: " + event.error);

console.log(event);

};

} catch(err) {

console.log(err);

alert(err);

}

}