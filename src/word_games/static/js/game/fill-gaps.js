const sentencesLimit = 16;
let sentencesCounter = 0;

new Sortable(document.querySelector('#editor'), {
    handle: '.drag-handle',
    animation: 150
});

const gameContainer =document.getElementById("game")
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
    for (const [sentence, values] of Object.entries(editorInitState).reverse()) {
        addSentence();
        const sentencesInputs = editorContainer.querySelectorAll(".input");
        const last_sentence = sentencesInputs[sentencesInputs.length - 1];
        last_sentence.textContent = sentence;
        for (const range of values){
            wrapRange(last_sentence, range["start"], range["end"] + 1)
        }
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
        sentences[el.textContent] = getMarkedPositions(el);
    });
    return JSON.stringify(sentences);
}

function getMarkedPositions (container) {
    const indices = [];
    let offset = 0;
    const walker = document.createTreeWalker(
        container,
        NodeFilter.SHOW_TEXT,
    );
    while (walker.nextNode()) {
        const node = walker.currentNode;
        const parent = node.parentElement;
        if (parent?.matches("span.marked")) {
            const next_start = offset;
            const next_end = offset + node.textContent.length - 1;
            if (next_start > next_end){
                console.log("Nested spans encountered. Skipping.");
            }
            const prev_span = indices.at(-1) ?? {"start": -2, "end": -2};
            if (next_start <= prev_span["end"] + 1){
                indices[indices.length - 1] = {
                    start: prev_span["start"],
                    end: Math.max(prev_span["end"], next_end),
                }
            }
            else{
                indices.push({
                start: offset,
                end: offset + node.textContent.length - 1
            });
            }
        }
        offset += node.textContent.length;
    }
    return indices;
}


function wrapRange(element, start, end, class_="marked") {
    const text = element.textContent;
    const before = text.slice(0, start);
    const selected = text.slice(start, end);
    const after = text.slice(end);
    element.innerHTML =
        `${before}<span class=${class_}>${selected}</span>${after}`;
}

initEditor();
