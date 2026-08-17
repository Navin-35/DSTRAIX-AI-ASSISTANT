import React, { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;


function App() {

  // ==========================================================
  // CHAT STATE
  // ==========================================================

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);


  // ==========================================================
  // MODE
  // ==========================================================

  const [mode, setMode] = useState("chat");


  // ==========================================================
  // CONVERSATION
  // ==========================================================

  const [conversationId] = useState(
    () => `conversation-${Date.now()}`
  );


  // ==========================================================
  // DOCUMENT STATE
  // ==========================================================

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [storeName, setStoreName] =
    useState("");

  const [uploading, setUploading] =
    useState(false);

  const [documentStatus, setDocumentStatus] =
    useState("");


  // ==========================================================
  // ADD MESSAGE
  // ==========================================================

  const addMessage = (
    role,
    content
  ) => {

    setMessages(
      previous => [
        ...previous,
        {
          role,
          content
        }
      ]
    );

  };


  // ==========================================================
  // STREAMING CHAT
  // ==========================================================

  const sendStreamingMessage = async () => {

    if (!input.trim() || loading) {
      return;
    }


    const currentMessage =
      input.trim();


    setInput("");

    setLoading(true);


    // --------------------------------------------------------
    // Add user message
    // --------------------------------------------------------

    setMessages(
      previous => [
        ...previous,

        {
          role: "user",
          content: currentMessage
        },

        {
          role: "assistant",
          content: ""
        }
      ]
    );


    try {

      const response = await fetch(
        `${API_URL}/chat/stream`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            message: currentMessage,

            conversation_id:
              conversationId
          })
        }
      );


      // ------------------------------------------------------
      // HTTP ERROR
      // ------------------------------------------------------

      if (!response.ok) {

        throw new Error(
          `Server error: ${response.status}`
        );

      }


      // ------------------------------------------------------
      // STREAM CHECK
      // ------------------------------------------------------

      if (!response.body) {

        throw new Error(
          "Streaming is not supported by this browser."
        );

      }


      // ------------------------------------------------------
      // STREAM READER
      // ------------------------------------------------------

      const reader =
        response.body.getReader();


      const decoder =
        new TextDecoder();


      let assistantText = "";


      // ------------------------------------------------------
      // READ CHUNKS
      // ------------------------------------------------------

      while (true) {

        const {
          value,
          done
        } = await reader.read();


        if (done) {
          break;
        }


        const chunk =
          decoder.decode(
            value,
            {
              stream: true
            }
          );


        assistantText += chunk;


        // ----------------------------------------------------
        // Update the last assistant message
        // ----------------------------------------------------

        setMessages(
          previous => {

            const updated =
              [...previous];


            updated[
              updated.length - 1
            ] = {

              role: "assistant",

              content:
                assistantText

            };


            return updated;

          }
        );

      }


    } catch (error) {

      console.error(
        "Streaming error:",
        error
      );


      setMessages(
        previous => {

          const updated =
            [...previous];


          updated[
            updated.length - 1
          ] = {

            role: "assistant",

            content:
              `❌ ${error.message}`

          };


          return updated;

        }
      );


    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // AGENT MESSAGE
  // ==========================================================

  const sendAgentMessage = async () => {

    if (!input.trim() || loading) {
      return;
    }


    const currentMessage =
      input.trim();


    setInput("");

    setLoading(true);


    setMessages(
      previous => [
        ...previous,

        {
          role: "user",
          content: currentMessage
        },

        {
          role: "assistant",
          content: ""
        }
      ]
    );


    try {

      const response =
        await fetch(
          `${API_URL}/agent/`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              message:
                currentMessage
            })
          }
        );


      if (!response.ok) {

        const errorText =
          await response.text();

        throw new Error(
          errorText
        );

      }


      const data =
        await response.json();


      const answer =
        data.response ||
        "No response received.";


      setMessages(
        previous => {

          const updated =
            [...previous];


          updated[
            updated.length - 1
          ] = {

            role: "assistant",

            content: answer

          };


          return updated;

        }
      );


    } catch (error) {

      console.error(
        "Agent error:",
        error
      );


      setMessages(
        previous => {

          const updated =
            [...previous];


          updated[
            updated.length - 1
          ] = {

            role: "assistant",

            content:
              `❌ ${error.message}`

          };


          return updated;

        }
      );


    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // DOCUMENT QUESTION
  // ==========================================================

  const askDocument = async () => {

    if (!input.trim() || loading) {
      return;
    }


    if (!storeName) {

      addMessage(
        "assistant",
        "❌ Please upload a document first."
      );

      return;

    }


    const currentMessage =
      input.trim();


    setInput("");

    setLoading(true);


    setMessages(
      previous => [
        ...previous,

        {
          role: "user",
          content: currentMessage
        },

        {
          role: "assistant",
          content: ""
        }
      ]
    );


    try {

      const response =
        await fetch(
          `${API_URL}/documents/ask`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              question:
                currentMessage,

              store_name:
                storeName
            })
          }
        );


      if (!response.ok) {

        const errorText =
          await response.text();

        throw new Error(
          errorText
        );

      }


      const data =
        await response.json();


      const answer =
        data.answer ||
        data.response ||
        "No answer received.";


      setMessages(
        previous => {

          const updated =
            [...previous];


          updated[
            updated.length - 1
          ] = {

            role: "assistant",

            content: answer

          };


          return updated;

        }
      );


    } catch (error) {

      console.error(
        "Document error:",
        error
      );


      setMessages(
        previous => {

          const updated =
            [...previous];


          updated[
            updated.length - 1
          ] = {

            role: "assistant",

            content:
              `❌ ${error.message}`

          };


          return updated;

        }
      );


    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // MAIN SEND FUNCTION
  // ==========================================================

  const sendMessage = async () => {

    if (mode === "chat") {

      await sendStreamingMessage();

      return;

    }


    if (mode === "agent") {

      await sendAgentMessage();

      return;

    }


    if (mode === "document") {

      await askDocument();

      return;

    }

  };


  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyDown = (
    event
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();

    }

  };


  // ==========================================================
  // CREATE DOCUMENT STORE
  // ==========================================================

  const createDocumentStore =
    async () => {

      const response =
        await fetch(
          `${API_URL}/documents/store?name=DSTRAIX%20Knowledge%20Base`,
          {
            method: "POST"
          }
        );


      if (!response.ok) {

        throw new Error(
          "Failed to create document store."
        );

      }


      const data =
        await response.json();


      const newStore =
        data.store_name;


      setStoreName(
        newStore
      );


      return newStore;

    };


  // ==========================================================
  // UPLOAD DOCUMENT
  // ==========================================================

  const uploadDocument =
    async () => {

      if (!selectedFile) {

        setDocumentStatus(
          "Please select a file first."
        );

        return;

      }


      setUploading(true);

      setDocumentStatus(
        "Creating knowledge store..."
      );


      try {

        const newStore =
          await createDocumentStore();


        setDocumentStatus(
          "Uploading and indexing document..."
        );


        const formData =
          new FormData();


        formData.append(
          "file",
          selectedFile
        );


        const response =
          await fetch(
            `${API_URL}/documents/upload?store_name=${encodeURIComponent(
              newStore
            )}`,
            {
              method: "POST",

              body: formData
            }
          );


        if (!response.ok) {

          const errorText =
            await response.text();

          throw new Error(
            errorText
          );

        }


        setDocumentStatus(
          `✓ ${selectedFile.name} uploaded successfully`
        );


        setMode("document");


      } catch (error) {

        console.error(
          "Upload error:",
          error
        );


        setDocumentStatus(
          `❌ ${error.message}`
        );


      } finally {

        setUploading(false);

      }

    };


  // ==========================================================
  // CLEAR CHAT
  // ==========================================================

  const clearChat = async () => {

    try {

      await fetch(
        `${API_URL}/chat/${conversationId}`,
        {
          method: "DELETE"
        }
      );

    } catch (error) {

      console.error(
        "Clear conversation error:",
        error
      );

    }


    setMessages([]);

  };


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="app">


      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="header">


        <div className="brand">

          <div className="brand-logo">
            D
          </div>

          <div>

            <h1>
              DSTRAIX
            </h1>

            <span>
              AI Assistant
            </span>

          </div>

        </div>


        {/* MODE SELECTOR */}

        <div className="mode-selector">


          <button
            className={
              mode === "chat"
                ? "mode-button active"
                : "mode-button"
            }

            onClick={() =>
              setMode("chat")
            }
          >
            💬 Chat
          </button>


          <button
            className={
              mode === "agent"
                ? "mode-button active"
                : "mode-button"
            }

            onClick={() =>
              setMode("agent")
            }
          >
            🤖 Agent
          </button>


          <button
            className={
              mode === "document"
                ? "mode-button active"
                : "mode-button"
            }

            onClick={() =>
              setMode("document")
            }
          >
            📚 Document
          </button>


        </div>


        <div className="header-right">

          <span className="online-dot">
            ●
          </span>

          <span>
            Online
          </span>

        </div>


      </header>


      {/* ================================================== */}
      {/* CHAT */}
      {/* ================================================== */}

      <main className="chat-container">


        {/* WELCOME */}

        {messages.length === 0 && (

          <div className="welcome">

            <div className="welcome-icon">
              ✦
            </div>


            <h2>
              Welcome to DSTRAIX
            </h2>


            <p>
              Your intelligent AI assistant
              for conversations, documents
              and intelligent tasks.
            </p>


            <div className="feature-cards">


              <div
                className="feature-card"

                onClick={() =>
                  setMode("chat")
                }
              >

                <div>
                  💬
                </div>

                <h3>
                  Chat
                </h3>

                <p>
                  Ask anything and receive
                  instant streaming answers.
                </p>

              </div>


              <div
                className="feature-card"

                onClick={() =>
                  setMode("agent")
                }
              >

                <div>
                  🤖
                </div>

                <h3>
                  Agent
                </h3>

                <p>
                  Let DSTRAIX use tools
                  to solve tasks.
                </p>

              </div>


              <div
                className="feature-card"

                onClick={() =>
                  setMode("document")
                }
              >

                <div>
                  📚
                </div>

                <h3>
                  RAG
                </h3>

                <p>
                  Ask questions about
                  your documents.
                </p>

              </div>


            </div>

          </div>

        )}


        {/* MESSAGES */}

        <div className="messages">


          {messages.map(
            (message, index) => (

              <div
                key={index}

                className={
                  message.role === "user"
                    ? "message user-message"
                    : "message assistant-message"
                }
              >


                <div className="avatar">

                  {message.role === "user"
                    ? "You"
                    : "D"}

                </div>


                <div className="message-body">


                  <div className="message-name">

                    {message.role === "user"
                      ? "You"
                      : "DSTRAIX"}

                  </div>


                  <div className="message-content">

                    {message.content}

                    {loading &&
                      index ===
                        messages.length - 1 &&
                      message.role ===
                        "assistant" && (

                        <span className="cursor">
                          ▌
                        </span>

                      )}

                  </div>


                </div>


              </div>

            )
          )}


          {/* THINKING */}

          {loading &&
            messages.length === 0 && (

              <div className="message assistant-message">

                <div className="avatar">
                  D
                </div>

                <div className="message-body">

                  <div className="message-name">
                    DSTRAIX
                  </div>

                  <div className="message-content">

                    Thinking...

                  </div>

                </div>

              </div>

            )}


        </div>

      </main>


      {/* ================================================== */}
      {/* DOCUMENT UPLOAD */}
      {/* ================================================== */}

      <section className="document-section">


        <div className="document-upload">


          <label className="file-label">

            📎

            <span>

              {selectedFile
                ? selectedFile.name
                : "Choose PDF / TXT / MD / DOCX"}

            </span>


            <input
              type="file"

              accept=".pdf,.txt,.md,.docx"

              onChange={
                (event) => {

                  setSelectedFile(
                    event.target.files?.[0] ||
                    null
                  );

                  setDocumentStatus("");

                }
              }
            />

          </label>


          <button
            className="upload-button"

            onClick={
              uploadDocument
            }

            disabled={
              uploading ||
              !selectedFile
            }
          >

            {uploading
              ? "Uploading..."
              : "Upload"}

          </button>


          {documentStatus && (

            <span className="document-status">

              {documentStatus}

            </span>

          )}


        </div>


      </section>


      {/* ================================================== */}
      {/* INPUT */}
      {/* ================================================== */}

      <section className="input-section">


        <div className="input-box">


          <textarea

            value={input}

            onChange={
              (event) =>
                setInput(
                  event.target.value
                )
            }

            onKeyDown={
              handleKeyDown
            }

            placeholder={

              mode === "chat"
                ? "Ask DSTRAIX anything..."

                : mode === "agent"
                ? "Ask the DSTRAIX agent..."

                : "Ask something about your document..."

            }

            rows="1"

          />


          <button

            className="send-button"

            onClick={
              sendMessage
            }

            disabled={
              loading ||
              !input.trim()
            }

          >

            ➤

          </button>


        </div>


        <div className="input-footer">


          <span>

            Mode:

            {" "}

            <strong>

              {mode === "chat"
                ? "Streaming Chat"

                : mode === "agent"
                ? "AI Agent"

                : "Document RAG"}

            </strong>

          </span>


          <button
            className="clear-button"

            onClick={
              clearChat
            }
          >

            Clear chat

          </button>


        </div>


      </section>


    </div>

  );
}


export default App;