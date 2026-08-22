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
const restoreButtonTemplate = document.getElementById("restore-template")
const gameData = document.getElementById("content");

let brushMode = false;

function initEditor(){
    if (editorInitState === null){
        console.log("Fresh editor state.")
        return;
    }
    if (!isDict(editorInitState)){
        console.log("Editor init state is corrupted.")
        return;
    }
    for (const [sentence, value] of Object.entries(editorInitState).reverse()) {
        addSentence();
        const sentencesInputs = editorContainer.querySelectorAll(".input");
        const last_sentence = sentencesInputs[sentencesInputs.length - 1];
        last_sentence.textContent = sentence;

    }
}

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
    editButton.addEventListener("click", (event) => {
        event.preventDefault();
        brushMode = !brushMode;
        sentenceField.classList.toggle("brush-mode", brushMode);
        editButton.classList.toggle("active", brushMode);
    });
    sentenceField.addEventListener("pointerup", (event) => {
        event.preventDefault();
        if (!brushMode) return;
        if (event.pointerType !== "mouse" && event.pointerType !== "pen") return;
        const selection = window.getSelection();
        if (!selection.rangeCount || selection.isCollapsed) return;
        const range = selection.getRangeAt(0);
        if (!sentenceField.contains(range.commonAncestorContainer)) return;
        const marked = document.createElement("span");
        marked.classList.add("marked")
        try {
            range.surroundContents(marked);
        } catch (error) {
            console.warn("Selection crosses multiple elements.", error);
        }
        selection.removeAllRanges();
        brushMode = false;
        sentenceField.classList.remove("brush-mode");
        editButton.classList.remove("active");
    })
    const deleteButton = removeButtonTemplate.cloneNode(true);
    deleteButton.classList.remove("dummy");
    deleteButton.classList.add("delete")
    deleteButton.addEventListener('click', (event) => {
        event.preventDefault();
        deleteButton.parentElement.remove();
    });
    const restoreButton = restoreButtonTemplate.cloneNode(true);
    restoreButton.classList.remove("dummy");
    restoreButton.classList.add("restore");
    restoreButton.addEventListener("click", (event) => {
        event.preventDefault();
        sentenceField.querySelectorAll("span").forEach(span => {
        span.replaceWith(...span.childNodes);
        });
    });

    sentenceRow.classList.add("row")
    for (el of [dragSpan, sentenceField, editButton, restoreButton, deleteButton]) {
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

function isDict(value){
    return (value !== undefined && value !== null && value.constructor == Object)
}

addButton.addEventListener("click", (event) => {
    event.preventDefault();
    addSentence();
});

document.querySelector("form").addEventListener("submit", ()=> {
    gameData.value = getGameContent();
});


function getGameContent(){
    let sentences = {};
    if (editorContainer.querySelector(".input") === null){
        return "";
    }
    editorContainer.querySelectorAll(".input").forEach((el) => {
        sentences[el.textContent] = [];
        el.querySelectorAll(".marked").forEach((marked)=>{
            sentences[el.textContent].push(marked.textContent)
        });
    });
    return JSON.stringify(sentences);
}

initEditor();
