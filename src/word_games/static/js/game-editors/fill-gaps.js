const sentencesLimit = 16;
let sentencesCounter = 0;

new Sortable(document.querySelector('#editor'), {
    handle: '.drag-handle',
    animation: 150
});

const editorContainer =document.getElementById("editor")
const addButton = document.getElementById("addNew")
const editButtonTemplate = document.getElementById("edit-template")
const removeButtonTemplate = document.getElementById("remove-template")

function addSentence(){
    if (sentencesCounter >= sentencesLimit) {
        console.log("Sentences limit per game reached.");
        return
    }
    let sentenceField = document.createElement("div");
    sentenceField.contentEditable = true;
    sentenceField.classList.add("input");
    let dragSpan = document.createElement("span");
    dragSpan.textContent = "⠿";
    dragSpan.classList.add("drag-handle");
    let sentenceRow = document.createElement("div")
    const editButton = editButtonTemplate.cloneNode(true);
    editButton.classList.remove("dummy");
    editButton.classList.add("edit");
    editButton.addEventListener("click", () => {
        brushMode = !brushMode;
        sentenceField.classList.toggle("brush-mode", brushMode);

    });
    const deleteButton = removeButtonTemplate.cloneNode(true);
    deleteButton.classList.remove("dummy");
    deleteButton.classList.add("delete")
    deleteButton.addEventListener('click', () => {
        deleteButton.parentElement.remove();
    });
    sentenceRow.classList.add("row")
    for (el of [dragSpan, sentenceField, editButton, deleteButton]) {
        sentenceRow.appendChild(el);
    }
    editorContainer.insertBefore(sentenceRow, editorContainer.lastElementChild);
    updateSentenceCounter();
}


function updateSentenceCounter(){
    sentencesCounter += 1;
    if (sentencesCounter >= sentencesLimit) {
        disableAddButton();
    }
}

function disableAddButton(){
    addButton.disabled = true;
}

function enableAddButton(){
    addButton.removeAttribute("disabled")
}

addButton.addEventListener("click", addSentence);
