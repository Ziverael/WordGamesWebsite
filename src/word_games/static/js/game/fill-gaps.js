const gameContainer = document.getElementById("game")
const gameData = document.getElementById("content");

function initGame() {
    gameContainer.querySelectorAll(".sentence").forEach((el) => {
        el.innerHTML = el.innerHTML.replace(
            /\*\*(\d+\.\d+)\*\*/g,
            (_, idx) => {
                return `<input type="text" name="${idx}" class="sentence-input inline">`;
            }
        );
    });
}

function showAnswers () {
    if (answerCorrectPairs === null){
        console.warn("Answers not collected.");
        return
    }
    sentencesFields = gameContainer.querySelectorAll(".sentence");
    let answerIter = 0;
    for (const sentenceField of sentencesFields) {
        sentenceField.innerHTML = sentenceField.innerHTML.replace(
            /\*\*(\d+\.\d+)\*\*/g,
            (_, idx) => {
                const pair = answerCorrectPairs[idx];
                if (!pair) {
                    console.warn("No answer pair for placeholder");
                    return "***";
                }
                const correctAnswer = pair["expected"];
                const userAnswer = pair["given"];
                return userAnswer == correctAnswer
                    ? `<span class="correct">${correctAnswer}</span>`
                : `<span class="wrong">${userAnswer}</span><span class="expected">(${correctAnswer})</span>`;
        });
    }
}

function disableInput(inputElement){
    inputElement.disabled = true;
}

function setInputValue(inputElement, value){

}

function displayElementAnswer (inputElement, userInput, correctAnswer){
    inputElement.value
}

function setTextColor(){}

console.log(isSolved);
if ( isSolved ){
    showAnswers();
}
else{
    initGame();
}
