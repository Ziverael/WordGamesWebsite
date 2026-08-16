function renderEditor() {
    const selectedType = layoutOptions.value;
    switch(selectedType) {
    case "Crossword":
        console.log("Word")
        break;
    case "Sentences":
        console.log("Sentences")
        render_fill_gaps_sentences_editor()
        break;
    default:
    }

}

/**
 * Renders an editor for creating fill-in-the-gaps exercises where
 * gaps can contain arbitrary fragments of a sentence.
 *
 * The editor maintains:
 * - full_sentences: the complete sentences entered by the user.
 * - missing_mark_indexed: character-index ranges representing gaps
 *   in each sentence.
 *
 * @returns {HTMLElement} The root editor element.
 */
function render_fill_gaps_sentences_editor() {
    const full_sentences = [];
    const missing_mark_indexed = [];
    const root = document.createElement("div");
    root.className = "editor"

    const insert_new_sentence_button = document.createElement("button");
    insert_new_sentence_button.type = "button";
    insert_new_sentence_button.textContent = "Add sentence";

    const mark_as_gap_button = document.createElement("button");
    mark_as_gap_button.type = "button";
    mark_as_gap_button.textContent = "Mark as gap";

    const sentences_container = document.createElement("div");
    sentences_container.className = "sentences-container";

    let marking_enabled = false;
    function get_character_range(element, range) {
        const pre_range = document.createRange();
        pre_range.selectNodeContents(element);
        pre_range.setEnd(range.startContainer, range.startOffset);

        const start = pre_range.toString().length;
        const length = range.toString().length;

        return [start, start + length];
    }
    function add_gap(sentence_index, range) {
        if (!missing_mark_indexed[sentence_index]) {
            missing_mark_indexed[sentence_index] = [];
        }

        missing_mark_indexed[sentence_index].push(range);

        missing_mark_indexed[sentence_index].sort(
            ([a], [b]) => a - b
        );
    }


    function mark_selected_text(sentence_index, editor) {
        const selection = window.getSelection();

        if (!selection || selection.rangeCount === 0) {
            return;
        }

        const range = selection.getRangeAt(0);

        if (range.collapsed || !editor.contains(range.commonAncestorContainer)) {
            return;
        }

        const [start, end] = get_character_range(editor, range);

        if (start === end) {
            return;
        }

        add_gap(sentence_index, [start, end]);

        /*
         * Visually mark the selected fragment.
         */
        const fragment = range.extractContents();

        /** @type {HTMLSpanElement} */
        const gap = document.createElement("span");
        gap.className = "gap-mark";
        gap.style.textDecoration = "underline";
        gap.style.backgroundColor = "#ddd";

        gap.appendChild(fragment);
        range.insertNode(gap);

        selection.removeAllRanges();
    }

    /**
     * Creates a new sentence editor.
     *
     * @param {string} sentence
     * @param {number} sentence_index
     * @returns {HTMLElement}
     */
    function create_sentence_editor(sentence, sentence_index) {
        /** @type {HTMLDivElement} */
        const wrapper = document.createElement("div");
        wrapper.className = "sentence-wrapper";

        /** @type {HTMLDivElement} */
        const editor = document.createElement("div");
        editor.className = "sentence-editor";
        editor.contentEditable = "true";
        editor.spellcheck = true;
        editor.textContent = sentence;

        /** @type {HTMLButtonElement} */
        const delete_button = document.createElement("button");
        delete_button.type = "button";
        delete_button.textContent = "Delete";

        editor.addEventListener("input", () => {
            full_sentences[sentence_index] = editor.textContent ?? "";
        });

        editor.addEventListener("mouseup", () => {
            if (marking_enabled) {
                mark_selected_text(sentence_index, editor);
            }
        });

        delete_button.addEventListener("click", () => {
            full_sentences.splice(sentence_index, 1);
            missing_mark_indexed.splice(sentence_index, 1);

            render_sentences();
        });

        wrapper.appendChild(editor);
        wrapper.appendChild(delete_button);

        return wrapper;
    }

    /**
     * Re-renders all sentence editors.
     *
     * @returns {void}
     */
    function render_sentences() {
        sentences_container.innerHTML = "";

        full_sentences.forEach((sentence, index) => {
            sentences_container.appendChild(
                create_sentence_editor(sentence, index)
            );
        });
    }

    insert_new_sentence_button.addEventListener("click", () => {
        const sentence = window.prompt("Enter a sentence:");

        if (sentence === null || sentence.trim() === "") {
            return;
        }

        full_sentences.push(sentence);
        missing_mark_indexed.push([]);

        render_sentences();
    });

    mark_as_gap_button.addEventListener("click", () => {
        marking_enabled = !marking_enabled;

        mark_as_gap_button.classList.toggle(
            "active",
            marking_enabled
        );

        mark_as_gap_button.textContent = marking_enabled
            ? "Stop marking gaps"
            : "Mark as gap";

        sentences_container.classList.toggle(
            "marking-gaps",
            marking_enabled
        );
    });

    root.appendChild(insert_new_sentence_button);
    root.appendChild(mark_as_gap_button);
    root.appendChild(sentences_container);

    return root;
}


/**
 * Renders an editor for creating fill-in-the-gaps exercises where
 * individual words can be marked as missing.
 *
 * The editor maintains:
 * - full_words: the complete list of words.
 * - missing_mark_indexed: indices of words that should become gaps.
 *
 * Each word can optionally have an image associated with it.
 *
 * @returns {HTMLElement} The root editor element.
 */
function render_fill_gaps_words_editor() {
    /** @type {string[]} */
    const full_words = [];

    /**
     * Indices of words marked as gaps.
     *
     * @type {number[]}
     */
    const missing_mark_indexed = [];

    /**
     * Optional image associated with each word.
     *
     * @type {Array<string | null>}
     */
    const word_images = [];

    /** @type {HTMLElement} */
    const root = document.createElement("div");
    root.className = "editor"

    /** @type {HTMLButtonElement} */
    const insert_new_word_button = document.createElement("button");
    insert_new_word_button.type = "button";
    insert_new_word_button.textContent = "Add word";

    /** @type {HTMLButtonElement} */
    const mark_as_gap_button = document.createElement("button");
    mark_as_gap_button.type = "button";
    mark_as_gap_button.textContent = "Mark as gap";

    /** @type {HTMLDivElement} */
    const words_container = document.createElement("div");
    words_container.className = "words-container";

    let marking_enabled = false;

    /**
     * Creates an editor for a single word.
     *
     * @param {string} word
     * @param {number} word_index
     * @returns {HTMLElement}
     */
    function create_word_editor(word, word_index) {
        /** @type {HTMLDivElement} */
        const wrapper = document.createElement("div");
        wrapper.className = "word-wrapper";

        /** @type {HTMLInputElement} */
        const word_input = document.createElement("input");
        word_input.type = "text";
        word_input.value = word;
        word_input.placeholder = "Word";

        /** @type {HTMLInputElement} */
        const image_input = document.createElement("input");
        image_input.type = "url";
        image_input.placeholder = "Optional image URL";
        image_input.value = word_images[word_index] ?? "";

        /** @type {HTMLButtonElement} */
        const gap_button = document.createElement("button");
        gap_button.type = "button";
        gap_button.textContent = missing_mark_indexed.includes(word_index)
            ? "Remove gap"
            : "Mark gap";

        /** @type {HTMLButtonElement} */
        const delete_button = document.createElement("button");
        delete_button.type = "button";
        delete_button.textContent = "Delete";

        word_input.addEventListener("input", () => {
            full_words[word_index] = word_input.value;
        });

        image_input.addEventListener("input", () => {
            word_images[word_index] = image_input.value || null;
        });

        gap_button.addEventListener("click", () => {
            const gap_index = missing_mark_indexed.indexOf(word_index);

            if (gap_index === -1) {
                missing_mark_indexed.push(word_index);
                gap_button.textContent = "Remove gap";
            } else {
                missing_mark_indexed.splice(gap_index, 1);
                gap_button.textContent = "Mark gap";
            }

            wrapper.classList.toggle(
                "is-gap",
                missing_mark_indexed.includes(word_index)
            );
        });

        delete_button.addEventListener("click", () => {
            full_words.splice(word_index, 1);
            word_images.splice(word_index, 1);

            /*
             * Adjust gap indices after deleting a word.
             */
            for (let i = missing_mark_indexed.length - 1; i >= 0; i--) {
                if (missing_mark_indexed[i] === word_index) {
                    missing_mark_indexed.splice(i, 1);
                } else if (missing_mark_indexed[i] > word_index) {
                    missing_mark_indexed[i]--;
                }
            }

            render_words();
        });

        wrapper.appendChild(word_input);
        wrapper.appendChild(image_input);
        wrapper.appendChild(gap_button);
        wrapper.appendChild(delete_button);

        return wrapper;
    }

    /**
     * Re-renders all word editors.
     *
     * @returns {void}
     */
    function render_words() {
        words_container.innerHTML = "";

        full_words.forEach((word, index) => {
            words_container.appendChild(
                create_word_editor(word, index)
            );
        });
    }

    insert_new_word_button.addEventListener("click", () => {
        const word = window.prompt("Enter a word:");

        if (word === null || word.trim() === "") {
            return;
        }

        full_words.push(word.trim());
        word_images.push(null);

        render_words();
    });

    mark_as_gap_button.addEventListener("click", () => {
        marking_enabled = !marking_enabled;

        mark_as_gap_button.classList.toggle(
            "active",
            marking_enabled
        );

        mark_as_gap_button.textContent = marking_enabled
            ? "Stop marking gaps"
            : "Mark as gap";

        words_container.classList.toggle(
            "marking-gaps",
            marking_enabled
        );
    });

    root.appendChild(insert_new_word_button);
    root.appendChild(mark_as_gap_button);
    root.appendChild(words_container);

    return root;
}


layoutOptions.addEventListener("change", renderEditor)
